from app.config.settings import ApplicationSettings

try:
    print("Testing ApplicationSettings manually...")
    a = ApplicationSettings(name="  ")
    print("No error, name is:", repr(a.name))
except Exception as e:
    print("Caught expected exception:", type(e), e)
