from htdocs import webfaction
from myapp import main

application = webfaction.Middleware(main.app)
