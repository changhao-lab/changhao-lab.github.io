# 快速改动清单（最小步骤版）

> 目标：以后你只做最少改动，就能完成常见更新。

---

## A. 只改 Home 一句话

例如改首页第二段介绍：
1. 打开 `_data/site.yml`
2. 修改 `hero_paragraph_2`
3. 保存后本地刷新（或 push 到 GitHub）

---

## B. 只改 Open Positions 的一条岗位

1. 打开 `_data/positions.yml`
2. 在 `openings:` 里修改某一行
3. 保存并刷新

---

## C. 新增 1 位 Team 成员（最常用）

1. 打开 `_data/team.yml`
2. 在 `members:` 最后追加：

```yml
- name: New Member
  role: Ph.D. Student
  photo: assets/team/new-member.jpg
  photo_alt: Profile photo of new member
  photo_fallback: https://placehold.co/320x320/eaf4ff/1e4a73?text=Member
  email: new.member@example.com
```

3. 把照片放到 `assets/team/new-member.jpg`
4. 保存并刷新

---

## D. 新增 1 篇论文（最常用）

1. 打开 `_data/publications.yml`
2. 找到对应年份 `year:` 的 `items:`
3. 追加一条：

```yml
- authors: "A Author*, B Author, _Hao Chang_"
  title: Example Paper Title
  url: https://example-journal.org/paper
  journal: Example Journal
  doi: 10.1234/example.2026.001
```

4. 保存并刷新

---

## E. 只改 PI 信息

1. 打开 `_data/team.yml`
2. 修改 `pi:` 下字段（如 `name`、`title`、`research`、`email`）
3. 保存并刷新

---

## F. 只改页脚年份或文案

1. 打开 `_data/site.yml`
2. 修改 `footer_text`
3. 保存并刷新

---

## G. 本地看效果（必须）

不要双击 `index.html`。

在项目目录执行：

```bash
bundle install
bundle exec jekyll serve
```

浏览器打开：
- `http://127.0.0.1:4000/`

---

## H. push 后线上更新

1. `git add .`
2. `git commit -m "update content"`
3. `git push`
4. 等待 GitHub Pages 自动构建完成
