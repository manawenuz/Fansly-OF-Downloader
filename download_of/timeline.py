"""OnlyFans Timeline Scraping

Download timeline posts from OnlyFans creators.
Handles photos, videos, and GIFs.
"""

from curl_cffi import requests
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from config.onlyfans_config import OnlyFansConfig
from download.downloadstate import DownloadState
from textio import print_info, print_warning, print_error

PARALLEL_DOWNLOADS = 8


def download_timeline(config: OnlyFansConfig, state: DownloadState) -> None:
    """
    Download OnlyFans timeline posts

    Args:
        config: OnlyFans configuration
        state: Download state for this creator
    """
    # Track totals for progress reporting
    total_media = 0

    # GUI progress callback helper
    def send_progress(current, total, filename='', status='running'):
        if config.gui_mode and config.progress_callback:
            config.progress_callback({
                'type': 'timeline',
                'current': current,
                'total': total,
                'current_file': filename,
                'status': status,
                'duplicates': 0,
                'downloaded': total_media
            })

    try:
        api = config.get_api()

        print_info(f"\nDownloading timeline for: {state.creator_name}")

        # Ensure we have creator ID
        if not state.account_id:
            print_error("Creator ID not set. Run get_creator_account_info first.")
            return

        # Set download path: Downloads/CreatorName-of/Timeline/
        creator_folder = config.creator_folder_name(state.creator_name)
        timeline_folder = config.download_directory / creator_folder / "Timeline"
        timeline_folder.mkdir(parents=True, exist_ok=True)

        state.base_path = timeline_folder

        # Check if creator has download history (folder exists and has files)
        has_history = timeline_folder.exists() and any(timeline_folder.iterdir())

        # Check if post limit should be applied
        # Only apply to new creators when NOT in incremental mode
        apply_post_limit = (
            config.max_posts_per_creator is not None
            and not config.incremental_mode
            and not has_history
        )

        if apply_post_limit:
            print_info(f"Post limit enabled: Will download up to {config.max_posts_per_creator} newest posts for this new creator")

        before_cursor = None
        total_posts = 0
        page_num = 0

        while True:
            try:
                # Fetch posts
                response = api.get_timeline(
                    user_id=state.account_id,
                    limit=100,
                    before_publish_time=before_cursor
                )

                posts = response.get('list', [])

                if not posts:
                    print_info("No more posts to fetch")
                    break

                page_num += 1
                interval = getattr(config, 'page_progress_interval', 0)
                if interval > 0 and page_num % interval == 0:
                    print_info(f"Page {page_num}: processing {len(posts)} posts (total so far: {total_posts})...")

                # Collect all media items from this page of posts
                page_media = []
                for post in posts:
                    if config.stop_flag and config.stop_flag.is_set():
                        break
                    total_posts += 1
                    for media in parse_post_media(post, state):
                        media_type = media.get('type', 'unknown')
                        if media_type in ('photo', 'gif') and not config.download_photos:
                            continue
                        if media_type == 'video' and not config.download_videos:
                            continue
                        page_media.append(media)

                if config.stop_flag and config.stop_flag.is_set():
                    print_warning("Download stopped by user")
                    break

                # Download page media in parallel
                with ThreadPoolExecutor(max_workers=PARALLEL_DOWNLOADS) as pool:
                    futures = {
                        pool.submit(download_media_item, config, state, m): m
                        for m in page_media
                    }
                    for future in as_completed(futures):
                        if config.stop_flag and config.stop_flag.is_set():
                            pool.shutdown(wait=False, cancel_futures=True)
                            print_warning("Download stopped by user")
                            break
                        if future.result():
                            total_media += 1
                            send_progress(total_media, total_media, futures[future].get('filename', ''))

                # Check if post limit reached
                if apply_post_limit and total_posts >= config.max_posts_per_creator:
                    print_info(f"Reached post limit ({config.max_posts_per_creator} posts). Stopping timeline download.")
                    print_info(f"Downloaded content from {total_posts} posts for this new creator.")
                    break

                # Check for more posts
                has_more = response.get('hasMore', False)

                if not has_more:
                    print_info("Reached end of timeline")
                    break

                # Update cursor for next page
                # Use last post's publish time
                if posts:
                    last_post = posts[-1]
                    before_cursor = last_post.get('postedAtPrecise') or last_post.get('createdAt')

                # Rate limiting
                if config.rate_limit_delay > 0:
                    time.sleep(config.rate_limit_delay)

                # Check for stop flag (GUI support)
                if config.stop_flag and config.stop_flag.is_set():
                    print_warning("Download stopped by user")
                    break

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited
                    print_warning("Rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    raise

        print_info(f"\n✓ Timeline download complete!")
        print_info(f"  Posts processed: {total_posts}")
        print_info(f"  Media downloaded: {total_media}")

        # Send completion progress
        send_progress(
            current=total_media,
            total=total_media,
            filename='',
            status='complete'
        )

        state.pic_count = total_media

    except Exception as e:
        print_error(f"Timeline download failed: {e}")
        raise


def parse_post_media(post: Dict, state: DownloadState) -> List[Dict]:
    """
    Parse media items from OnlyFans post

    Args:
        post: Post data from API
        state: Download state

    Returns:
        List of media item dicts with url, filename, type
    """
    media_items = []
    post_id = post.get('id', 'unknown')

    # OF posts have 'media' array
    media_array = post.get('media', [])

    for idx, media in enumerate(media_array):
        media_id = media.get('id', idx)
        media_type = media.get('type', 'unknown')  # 'photo', 'video', 'gif', 'audio'

        # Get media URL
        # Check different possible URL locations
        media_url = None

        if 'source' in media:
            source = media['source']
            media_url = source.get('source') or source.get('url')

        if not media_url and 'files' in media:
            # Try files array
            files = media['files']
            if isinstance(files, dict):
                # Get highest quality
                for quality in ['source', 'full', 'preview']:
                    if quality in files:
                        media_url = files[quality].get('url')
                        if media_url:
                            break

        if not media_url:
            print_warning(f"Could not find media URL for {media_id}")
            continue

        # Determine file extension
        extension = get_media_extension(media_type, media_url)

        # Create filename: PostID_MediaID.ext
        filename = f"{post_id}_{media_id}.{extension}"

        media_items.append({
            'id': media_id,
            'type': media_type,
            'url': media_url,
            'filename': filename,
            'post_id': post_id,
        })

    return media_items


def download_media_item(config: OnlyFansConfig, state: DownloadState,
                        media: Dict) -> bool:
    """
    Download single media item — writes to WebDAV if configured, local disk otherwise.

    Returns:
        True if downloaded successfully, False if skipped
    """
    from download.webdav_client import get_client
    import tempfile

    filename = media['filename']
    dav = get_client()

    # Determine the relative path on WebDAV (mirrors local structure)
    # state.base_path is e.g. /Volumes/... or a local dir; we only need the
    # last two segments: <creator>-of/Timeline/<filename>
    rel_parts = state.base_path.parts[-2:]  # ('cherrylovebombb-of', 'Timeline')
    dav_rel = str(Path(*rel_parts) / filename)

    local_path = state.base_path / filename

    # --- Skip check: local first, then WebDAV ---
    if local_path.exists():
        if config.show_skipped_downloads:
            print_info(f"  ⊘ Skipping (local): {filename}")
        return False

    if dav and dav.exists(dav_rel):
        if config.show_skipped_downloads:
            print_info(f"  ⊘ Skipping (webdav): {filename}")
        return False

    try:
        if config.show_downloads:
            print_info(f"  ↓ Downloading: {filename}")

        response = requests.get(media['url'], stream=True, timeout=60, impersonate="chrome")
        response.raise_for_status()

        if dav:
            # Stream to a temp file, then PUT to WebDAV
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = Path(tmp.name)
                stopped = False
                for chunk in response.iter_content(chunk_size=8192):
                    if config.stop_flag and config.stop_flag.is_set():
                        stopped = True
                        break
                    if chunk:
                        tmp.write(chunk)

            if stopped:
                tmp_path.unlink(missing_ok=True)
                return False

            from download.webdav_client import _known_dirs
            dav.ensure_dirs(dav_rel, _known_dirs)
            dav.put(dav_rel, tmp_path)
            tmp_path.unlink(missing_ok=True)
        else:
            # Write locally
            stopped = False
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if config.stop_flag and config.stop_flag.is_set():
                        stopped = True
                        break
                    if chunk:
                        f.write(chunk)
            if stopped:
                local_path.unlink(missing_ok=True)
                return False

        return True

    except Exception as e:
        print_error(f"  ✗ Failed to download {filename}: {e}")
        if local_path.exists():
            local_path.unlink(missing_ok=True)
        return False


def get_media_extension(media_type: str, url: str) -> str:
    """
    Determine file extension from media type and URL

    Args:
        media_type: Type from API ('photo', 'video', 'gif', 'audio')
        url: Media URL

    Returns:
        File extension without dot
    """
    # Type-based mapping
    type_map = {
        'photo': 'jpg',
        'video': 'mp4',
        'gif': 'gif',
        'audio': 'mp3',
    }

    # Try type first
    if media_type in type_map:
        return type_map[media_type]

    # Try to extract from URL
    if '.' in url:
        parts = url.split('.')
        # Get last part before query string
        ext = parts[-1].split('?')[0].lower()
        # Validate it looks like an extension
        if len(ext) <= 4 and ext.isalnum():
            return ext

    # Default fallback
    return 'bin'
