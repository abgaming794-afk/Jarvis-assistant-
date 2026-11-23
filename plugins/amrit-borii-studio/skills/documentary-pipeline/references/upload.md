# Upload pack and YouTube upload

## Pack (`UPLOAD_PACK.md`)

- 3 title options (recommended first), thumbnail concept, description (hook paragraph, chapters, sources, credits,
  3 hashtags), tags, pinned comment with a question.
- Chapter timestamps come from the final video, including the 1.4 s pause added at each chapter card.
- Plain text for YouTube: strip markdown (`**`) from the description.

## Upload through vidIQ (channel @amritborii is connected)

1. Ask privacy (Private / Public / Schedule / Unlisted) and title before uploading; never choose privacy yourself.
2. `vidiq_social_account_list` (platform YOUTUBE) -> `platformAccountId`, check `canPublish`.
3. Thumbnail: `vidiq_upload_image` with no image -> PUT the JPG (under 2 MB) to `uploadUrl` with curl -> call again
   with `transferId` -> `imageId`.
4. Video: `vidiq_video_upload` with `localFile` (path, exact byte size, video/mp4; up to 4000 MB) -> run the returned
   command -> call again with `uploadId` until ready.
5. `vidiq_social_post_draft_create` with one YOUTUBE destination: title, description in `text`, tags (max 30,
   500 chars total), `privacyStatus`, `categoryId` 25 (News & Politics), `thumbnailImageId`, media = the video upload.
6. Show the draft to the user; publish with `vidiq_social_post_publish` only after they approve it; then
   `vidiq_social_post_status` until done and give the YouTube link.
7. Remind the user to set "Altered or synthetic content" in YouTube Studio if needed (AI voice), and to check the
   thumbnail was accepted (custom thumbnails need a verified channel).
