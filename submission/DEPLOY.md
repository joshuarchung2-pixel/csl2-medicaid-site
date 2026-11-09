# Deploy: GitHub Pages (staged, NOT run)

Nothing below has been run. Publishing needs Josh's go.

`gh` is already signed in as `joshuarchung2-pixel` (checked 2026-11-09 with `gh auth status`).

## 1. Create the public repo and push

```sh
cd ~/code/csl2-medicaid-site
gh auth status                      # confirm: joshuarchung2-pixel, active
git status                          # confirm: clean working tree on main
gh repo create joshuarchung2-pixel/csl2-medicaid-site \
  --public \
  --description "Medi-Cal enrollment guide for uninsured California families (CSL II educational project)" \
  --source=. --remote=origin --push
```

## 2. Turn on GitHub Pages from main, root folder

```sh
gh api -X POST repos/joshuarchung2-pixel/csl2-medicaid-site/pages \
  -f "source[branch]=main" -f "source[path]=/"
```

## 3. Wait for the build, then verify

```sh
gh api repos/joshuarchung2-pixel/csl2-medicaid-site/pages/builds/latest --jq .status   # repeat until "built"
curl -sI https://joshuarchung2-pixel.github.io/csl2-medicaid-site/ | head -1           # expect HTTP/2 200
curl -sI https://joshuarchung2-pixel.github.io/csl2-medicaid-site/es/index.html | head -1
```

## 4. Remove the "pending publish" tag from the submission PDF

```sh
cd ~/code/csl2-medicaid-site/submission
sed -i '' 's|<span class="pending">PENDING PUBLISH</span>||' pdf-source.html
~/agent-tools/mediasite-extract/.venv/bin/python3 make_pdf.py     # rewrites Chung_CSL2_Educational_Project.pdf
cd .. && git commit -am "Submission PDF: site is live" && git push
```

## 5. Canvas (Josh)

Upload `submission/Chung_CSL2_Educational_Project.pdf` to CSL II (course 3181), assignment 52434. Due Tue 11/17/2026, 11:59 PM PST.

## Notes

- `submission/shots/` is git-ignored, so the screenshots stay local and are not published.
- `.nojekyll` is included so Pages serves the files exactly as they are.
- The site loads nothing from third parties: no trackers, fonts, or CDNs. The self-check runs only in the browser.
