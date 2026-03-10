# Chang Hao Lab Website

Data-driven Jekyll website for **Chang Hao Lab**, ready for GitHub Pages.

## Project Structure
- `_config.yml` - Jekyll/GitHub Pages config
- `_layouts/default.html` - Shared page shell
- `_data/site.yml` - Site-level text (hero, footer, scholar link)
- `_data/research.yml` - Research module content
- `_data/publications.yml` - Publications data (authors, links, DOI)
- `_data/team.yml` - PI + member cards
- `_data/positions.yml` - Open positions module content
- `index.html` - Single-page template that renders all modules from `_data`
- `styles.css` / `script.js` - Styles and interactions

## Update Workflow (No HTML Editing Required)

### Update Research
Only edit:
- `_data/research.yml`

### Add/Edit Team Members
Only edit:
- `_data/team.yml` (`members` list)

### Update Publications
Only edit:
- `_data/publications.yml`

### Update Hero/Footer/Scholar Link
Only edit:
- `_data/site.yml`

### Update Open Positions
Only edit:
- `_data/positions.yml`

## Local Preview (Important)

Because this site uses Jekyll + Liquid templates, directly double-clicking `index.html` will not render correctly.

Use Jekyll local server instead:

1. Install Ruby (with `ridk` on Windows).
2. In this project folder, run:
	- `bundle install`
	- `bundle exec jekyll serve`
3. Open:
	- `http://127.0.0.1:4000/`

After editing files in `_data`, refresh browser to see updates.

## Deploy to GitHub Pages
1. Create a GitHub repository and push this project.
2. In GitHub repo: **Settings → Pages**.
3. Source: **Deploy from a branch**.
4. Branch: `main` (or `master`), folder: `/ (root)`.
5. Wait for build to finish; site will be available at your GitHub Pages URL.

## Free GitHub Domain
- Default free domain format:
	- `https://<username>.github.io/<repo>/`
- If this repo is named `<username>.github.io`, URL becomes:
	- `https://<username>.github.io/`

## Optional: Custom Domain
- Add a `CNAME` file in repo root with your domain (e.g. `lab.example.com`).
- Configure DNS in your domain provider.

## Scholar Profile
- https://scholar.google.com/citations?user=2YZzmdUAAAAJ&hl=en&oi=ao

## 中文维护指南
- 详细中文字段说明与修改示例：`DATA_EDIT_GUIDE_ZH.md`
- 最小步骤速查清单：`QUICK_EDIT_CHEATSHEET_ZH.md`
