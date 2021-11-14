import inspect
import os
import sys
import sysconfig


# ---------------------------------------------------- formatter base class

class Doc:
    PYTHONDOCS = os.environ.get("PYTHONDOCS",
                                "https://docs.python.org/%d.%d/library"
                                % sys.version_info[:2])

    def document(self, object,  name=None, *args):
        """Generate documentation for an object."""
        args = (object, name) + args

        # 'try' clause is to attempt to handle the possibility that inspect
        # identifies something in a way that pydoc itself has issues handling;
        # think 'super' and how it is a descriptor (which raises the exception
        # by lacking a __name__ attribute) and an instance.
        try:
            if inspect.ismodule(object): return self.docmodule(*args)
            if inspect.isclass(object): return self.docclass(*args)
            if inspect.isroutine(object): return self.docroutine(*args)
        except AttributeError:
            pass
        if inspect.isdatadescriptor(object): return self.docdata(*args)
        return self.docother(*args)

    def fail(self, object, name=None, *args):
        """Raise an exception for unimplemented types."""
        message = "don't know how to document object%s of type %s" % (
            name and ' ' + repr(name), type(object).__name__)
        raise TypeError(message)

    docmodule = docclass = docroutine = docother = docproperty = docdata = fail

    def getdocloc(self, object, basedir=sysconfig.get_path('stdlib')):
        """Return the location of module docs or None"""

        try:
            file = inspect.getabsfile(object)
        except TypeError:
            file = '(built-in)'

        docloc = os.environ.get("PYTHONDOCS", self.PYTHONDOCS)

        basedir = os.path.normcase(basedir)
        if (isinstance(object, type(os)) and
                (object.__name__ in ('errno', 'exceptions', 'gc', 'imp',
                                     'marshal', 'posix', 'signal', 'sys',
                                     '_thread', 'zipimport') or
                 (file.startswith(basedir) and
                  not file.startswith(os.path.join(basedir, 'site-packages')))) and
                object.__name__ not in ('xml.etree', 'test.pydoc_mod')):
            if docloc.startswith(("http://", "https://")):
                docloc = "{}/{}.html".format(docloc.rstrip("/"),
                                             object.__name__.lower())
            else:
                docloc = os.path.join(docloc, object.__name__.lower() + ".html")
        else:
            docloc = None
        return docloc
