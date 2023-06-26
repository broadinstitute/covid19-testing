Code for the [COVID-19 Diagnostic Processing Dashboard](https://covid19-testing.broadinstitute.org/)

### Development instructions
1. You will need a `data.json` file in the main level of the repository.
    - If you don't have this, you can download it from http://10.200.0.90:8090/api/latest/Covid19Dashboard. You will need to be on the VPN to do this if you're remote.
2. Make updates to `main_page_template.dev.html` and/or `daily_page_template.dev.html`.
3. Run `./build.test.site.sh`. This will update `index.test.html`, and `daily/index.test.html`.
4. Run a local server (e.g. `python3 -m http.server`) and check your changes at `/index.test.html` and/or `/daily/index.test.html`.
5. If everything looks good, `cp main_page_template.dev.html main_page_template.html` and/or `cp daily_page_template.dev.html daily_page_template.html`.
6. Push everything to the `main` branch. A script will automatically rebuild the production HTML pages every 5 minutes or so if there are data updates.