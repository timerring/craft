# Images in Issues and Comments

How to embed images in GitHub issue bodies and comments programmatically via the CLI.

## GitHub Contents API

Push image files to a branch in the same repo, then reference them with a URL that works for authenticated viewers.

**Step 1: Create a branch**

```bash
# Get the SHA of the default branch
SHA=$(gh api repos/{owner}/{repo}/git/ref/heads/main --jq '.object.sha')

# Create a new branch
gh api repos/{owner}/{repo}/git/refs -X POST \
  -f ref="refs/heads/{username}/images" \
  -f sha="$SHA"
```

**Step 2: Upload images via Contents API**

```bash
# Base64-encode the image and upload
BASE64=$(base64 -i /path/to/image.png)

gh api repos/{owner}/{repo}/contents/docs/images/my-image.png \
  -X PUT \
  -f message="Add image" \
  -f content="$BASE64" \
  -f branch="{username}/images" \
  --jq '.content.path'
```

Repeat for each image. The Contents API creates a commit per file.

**Step 3: Reference in markdown**

```markdown
![Description](https://github.com/{owner}/{repo}/raw/{username}/images/docs/images/my-image.png)
```

> **Important:** Use `github.com/{owner}/{repo}/raw/{branch}/{path}` format, NOT `raw.githubusercontent.com`. The `raw.githubusercontent.com` URLs return 404 for private repos. The `github.com/.../raw/...` format works because the browser sends auth cookies when the viewer is logged in and has repo access.

**Pros:** Works for any repo the viewer has access to, images live in version control, no expiration.
**Cons:** Creates commits, viewers must be authenticated, images won't render in email notifications or for users without repo access.

## Common pitfalls

- **`raw.githubusercontent.com` returns 404 for private repos** even with a valid token in the URL. GitHub's CDN does not pass auth headers through.
- **API download URLs are temporary.** URLs returned by `gh api repos/.../contents/...` with `download_url` include a token that expires.
- **Base64 encoding for large files** can hit API payload limits. The Contents API has a ~100MB file size limit but practical limits are lower for base64-encoded payloads.
- **Email notifications** will not render images that require authentication. If email readability requires public attachment hosting, report that the pure-`gh` workflow cannot provide it.
- **User-attachment uploads have no supported `gh` command.** If the task requires that hosting mode, report the limitation instead of switching tools.
