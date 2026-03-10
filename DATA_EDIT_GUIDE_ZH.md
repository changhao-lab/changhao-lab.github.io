# 数据文件修改指南（中文）

这个网站现在是“数据驱动”结构：
- 页面模板在 `index.html`（一般不用改）
- 内容数据在 `_data/*.yml`（日常只改这里）

---

## 1) Home 模块
编辑文件：`_data/site.yml`

常用字段：
- `kicker`：首页副标题（如 Biomedical Science · Brain-Gut Axis）
- `hero_title_line1`、`hero_title_line2`：首页主标题两行
- `hero_paragraph_1`、`hero_paragraph_2`：首页介绍正文
- `hero_image`：首页右侧图片路径
- `hero_image_alt`：图片替代文本
- `scholar_url`：Google Scholar 按钮链接
- `footer_text`：页脚文案

---

## 2) Research 模块
编辑文件：`_data/research.yml`

常用字段：
- `intro`：Research 模块开头一句话
- `cards`：三张研究卡片（可增减）
  - 每项含 `title`、`text`
- `focus_title`：Current Focus 标题
- `focus_items`：要点列表

---

## 3) Publications 模块
编辑文件：`_data/publications.yml`

结构说明：
- `years` 是年份分组列表
- 每个年份下 `items` 是论文列表
- 每篇论文字段：
  - `authors`：作者字符串（规则：通讯作者用 `*`，PI 名字用 `_Hao Chang_`）
  - `title`：论文标题
  - `url`：标题跳转链接（期刊正式页面）
  - `journal`：期刊名
  - `doi`：仅 DOI 号本体（不要带 `https://doi.org/`）

新增一篇论文示例（放到某个 `items` 下）：

```yml
- authors: "A Author*, B Author, _Hao Chang_"
  title: Example Paper Title
  url: https://example-journal.org/paper
  journal: Example Journal
  doi: 10.1234/example.2026.001
```

---

## 4) Team 模块
编辑文件：`_data/team.yml`

### PI 信息
在 `pi:` 下修改：
- `name`、`title`、`research`、`email`
- `photo`、`photo_fallback`

### 新增普通成员
在 `members:` 下新增一项（注意缩进）：

```yml
- name: New Member
  role: Ph.D. Student
  photo: assets/team/new-member.jpg
  photo_alt: Profile photo of new member
  photo_fallback: https://placehold.co/320x320/eaf4ff/1e4a73?text=Member
  email: new.member@example.com
```

---

## 5) Open Positions 模块
编辑文件：`_data/positions.yml`

常用字段：
- `intro`：模块介绍
- `openings_title`、`openings`：左侧岗位列表
- `special_title`、`special_paragraphs`：右侧说明文本
- `contact_email`：联系邮箱

---

## 6) 本地预览方式（不要双击 HTML）
因为使用了 Jekyll 模板，需用本地服务器渲染：

```bash
bundle install
bundle exec jekyll serve
```

打开：`http://127.0.0.1:4000/`

---

## 7) 常见错误排查
- 页面不更新：检查 `.yml` 缩进（必须统一空格缩进）
- 列表不显示：检查 `-` 是否与上级字段对齐
- PI 下划线失效：确认写成 `_Hao Chang_`
- 通讯作者星号失效：确认在作者名后加 `*`
