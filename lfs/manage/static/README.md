# How to build css from scss

- cd src/lfs/lfs/manage/static/lfs/manage
- sass scss/main.scss css/main.css --watch
- sass scss/main.scss css/main.css --style compressed --no-source-map --watch

# How to download vendor apps (for now, we'll bundle later)
- cd src/lfs/lfs/manage
- npm run setup