# Upload pack and YouTube upload

## Pack (`UPLOAD_PACK.md`)

- 3 title options (recommended first), thumbnail concept, description (hook paragraph, chapters, sources, credits,
  3 hashtags), tags, pinned comment with a question.
- Chapter timestamps come from the final video, including the 1.4 s pause added at each chapter card.
- Plain text for YouTube: strip markdown (`**`) from the description.

## Upload through vidIQ (channel @itsamritbori is connected)

1. Ask privacy (Private / Public / Schedule / Unlisted) and title before uploading; never choose privacy yourself.
2. `vidiq_social_account_list` (platform YOUTUBE) -> `platformAccountId`, check `canPublish`.
3. Thumbnail: `vidiq_upload_image` with no image -> PUT the JPG (under 2 MB) to `uploadUrl` with curl -> call again
   with `transferId` -> `imageId`.
4. Video: `vidiq_video_upload` with `localFile` (path, exact byte size, video/mp4; up to 4000 MB) -> run the returned
   command -> call again with `uploadId` until ready.
5. `vidiq_social_post_draft_create` with one YOUTUBE destination: title, description in `text`, tags (max 30,
   500 chars total), `privacyStatus`, `categoryId` 27 (Education, history) or 25 (News & Politics), `thumbnailImageId`, media = the video upload.
6. Show the draft to the user; publish with `vidiq_social_post_publish` only after they approve it; then
   `vidiq_social_post_status` until done and give the YouTube link.
7. Remind the user to set "Altered or synthetic content" in YouTube Studio if needed (AI voice), and to check the
   thumbnail was accepted (custom thumbnails need a verified channel).

## 1.0.0 notes (first direct upload, Khilafat, Nov 2026)

- Channel row: `vidiq_user_channels` / `vidiq_social_account_list` -> AMRIT BORI, handle @itsamritbori.
- A 1.4 GB master uploads fine with `localFile` (the returned shell command, run in the background, ~5-10 min);
  YouTube processing then shows 0-100 % in `vidiq_social_post_status` (poll every ~2-3 min, not every 10 s).
- Remove project-only lines from the description (e.g. "research/DOSSIER.md"): viewers cannot open them.
- After publishing, write the link into `UPLOAD_PACK.md` and commit. Tell the user that 4K processing on YouTube takes
  1-2 hours and what to set in Studio (Altered or synthetic content = Yes for AI voice/images, thumbnail check,
  pinned comment, Public when happy).
- Thumbnail swap later: `vidiq_update_video_thumbnail` (5 credits, HTTPS URL or data URI). If vidIQ says
  "Not enough credits", stop calling paid vidIQ tools and give the Studio steps instead.
