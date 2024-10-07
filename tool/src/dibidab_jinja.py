import jinja2
import pathlib

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(str(pathlib.Path(__file__).parent.absolute()) + "/jinja")
)
