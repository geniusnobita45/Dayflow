import runpy


module = runpy.run_path("app.py", run_name="dayflow_app")
module["app"].run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
