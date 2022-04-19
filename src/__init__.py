# vim: set expandtab shiftwidth=4 softtabstop=4:
import os

from chimerax.core.toolshed import BundleAPI


# Subclass from chimerax.core.toolshed.BundleAPI and
# override the method for registering commands,
# inheriting all other methods from the base class.
from chimerax.toolbar.manager import ToolbarManager


class _MyAPI(BundleAPI):

    api_version = 1     # register_command called with BundleInfo and
                        # CommandInfo instance instead of command name
                        # (when api_version==0)
    # Override method
    @staticmethod
    def start_tool(session, bi, ti):
        # session is an instance of chimerax.core.session.Session
        # bi is an instance of chimerax.core.toolshed.BundleInfo
        # ti is an instance of chimerax.core.toolshed.ToolInfo
        # This method is called once for each time the tool is invoked.
        # We check the name of the tool, which should match one of the
        # ones listed in bundle_info.xml (without the leading and
        # trailing whitespace), and create and return an instance of the
        # appropriate class from the ``tool`` module.
        if ti.name == "BED Models":
            from .BedModelsTool import tool
            return tool.BedModelsTool(session, ti.name)
        elif ti.name == "Bead Overlap":
            from .OverlapTool import tool
            return tool.OverlapTool(session, ti.name)
        elif ti.name == "Genome Distances":
            from .DistanceTool import tool
            return tool.DistanceTool(session, ti.name)
        elif ti.name == "Selector":
            from .SelectionTool import tool
            return tool.SelectionTool(session, ti.name)
        raise ValueError("trying to start unknown tool: %s" % ti.name)

    @staticmethod
    def get_class(class_name):
        # class_name will be a string
        if class_name == "BedModelsTool":
            from .BedModelsTool import tool
            return tool.BedModelsTool
        raise ValueError("Unknown class name '%s'" % class_name)

    # Override method
    @staticmethod
    def run_provider(session, name, mgr, **kw):
        # name is name of provider
        # mgr is manager
        # kw (keyword arguments) listed in the bundle_info.xml
        from chimerax.core.commands import run
        if isinstance(mgr, ToolbarManager):
            if name == "Models from Chromosomes":
                run(session, "genometools_make_submodels")
            elif name == "Model from Selection":
                run(session, "genometools_make_model_from_selection selection_model")
            elif name == "Inspect Beads":
                run(session, "genometools_inspect_beads")
            elif name == "Highlight":
                run(session, "genometools_highlight")
            elif name == "Bed Models":
                run(session, "ui tool show \"BED Models\"")
            elif name == "Bead Overlap":
                run(session, "ui tool show \"Bead Overlap\"")
            elif name == "Genome Distance":
                run(session, "ui tool show \"Genome Distance\"")
            elif name == "Selector":
                run(session, "ui tool show \"Selector\"")

        pass

    # Override method
    @staticmethod
    def register_command(bi, ci, logger):
        # bi is an instance of chimerax.core.toolshed.BundleInfo
        # ci is an instance of chimerax.core.toolshed.CommandInfo
        # logger is an instance of chimerax.core.logger.Logger

        # This method is called once for each command listed
        # in bundle_info.xml.  Since we only listed one command,
        # we expect only a single call to this method.

        # We import the function to call and its argument
        # description from the ``cmd`` module, adding a
        # synopsis from bundle_info.xml if none is supplied
        # by the code.
        #print("TEST" + os.getcwd())
        from . import cmd
        if ci.name == "genometools_highlight":
            func = cmd.highlight
            desc = cmd.highlight_desc
        elif ci.name == "genometools_visualise_bed":
            from .BedModelsTool import cmd
            func = cmd.visualise_bed
            desc = cmd.visualise_bed_desc
        elif ci.name == "genometools_inspect_beads":
            func = cmd.dump_bead_data
            desc = cmd.dump_bead_data_desc
        elif ci.name == "genometools_select_chromosome":
            func = cmd.select_chromosome
            desc = cmd.select_chromosome_desc
        elif ci.name == "genometools_make_submodels":
            func = cmd.make_submodels
            desc = cmd.make_submodels_desc
        elif ci.name == "genometools_make_model_from_selection":
            func = cmd.make_model_from_selection
            desc = cmd.make_model_from_selection_desc
        elif ci.name == "genometools_select":
            func = cmd.select_beads
            desc = cmd.select_beads_desc
        # TODO remove test
        elif ci.name == "genometools_test":
            func = cmd.test
            desc = cmd.test_desc
        # elif ci.name == "tutorial highlight":
        #     func = cmd.highlight
        #     desc = cmd.highlight_desc
        else:
            raise ValueError("trying to register unknown command: %s" % ci.name)

        if desc.synopsis is None:
            desc.synopsis = ci.synopsis

        # We then register the function as the command callback
        # with the chimerax.core.commands module.
        # Note that the command name registered is not hardwired,
        # but actually comes from bundle_info.xml.  In this example,
        # the command name is "hello", not "hello world".
        from chimerax.core.commands import register
        register(ci.name, desc, func)


# Create the ``bundle_api`` object that ChimeraX expects.
bundle_api = _MyAPI()
