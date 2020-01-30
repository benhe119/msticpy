# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""msticpy IPython magics."""
import re
from typing import List, Tuple

from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import line_cell_magic, Magics, magics_class

try:
    from bs4 import BeautifulSoup

    _BS_AVAILABLE = True
except ImportError:
    _BS_AVAILABLE = False

from ..sectools import base64unpack as base64
from ..sectools.iocextract import IoCExtract

from .._version import VERSION

__version__ = VERSION
__author__ = "Ian Hellen"


@magics_class
class Base64Magic(Magics):
    """Base64 IPython magic extension."""

    _STRIP_TAGS = r"</?decoded[^>]*>"

    @line_cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "--out", "-o", help="The variable to return the results in"
    )
    @magic_arguments.argument(
        "--pretty", "-p", help="Print formatted version of output", action="store_true"
    )
    @magic_arguments.argument(
        "--clean",
        "-c",
        help="Print decoded string with no formatting",
        action="store_true",
    )
    def b64(self, line: str = "", cell: str = None) -> str:
        """
        Base64 IPython magic extension.

        Parameters
        ----------
        line : str, optional
            Line contents, by default ""
        cell : str, optional
            Cell contents, by default None

        Returns
        -------
        str
            Decoded text

        """
        if cell is None:
            results, df_results = base64.unpack(line)

        else:
            results, df_results = base64.unpack(cell)
        args = magic_arguments.parse_argstring(self.b64, line)

        if args.clean:
            results = re.sub(self._STRIP_TAGS, "", results)
        elif args.pretty:
            if _BS_AVAILABLE:
                xml_str = f"<decoded_string>{results}</decoded_string>"
                b_soup = BeautifulSoup(xml_str, "xml")
                results = b_soup.prettify()
        print(results)
        if args.out is not None:
            self.shell.user_ns[args.out] = (results, df_results)
        return results


@magics_class
class IoCExtractMagic(Magics):
    """Ioc Extract IPython magic extension."""

    def __init__(self, shell):
        """
        Instantiate magic class.

        Parameters
        ----------
        shell : IPython shell
            IPython shell

        """
        # You must call the parent constructor
        super().__init__(shell)
        self._ioc_extract = IoCExtract()

    @line_cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "--out", "-o", help="The variable to return the results in"
    )
    def ioc(self, line="", cell=None) -> List[Tuple[str, List[str]]]:
        """
        Ioc Extract IPython magic extension.

        Parameters
        ----------
        line : str, optional
            Line contents, by default ""
        cell : str, optional
            Cell contents, by default None

        Returns
        -------
        List[Tuple[str, List[str]]]
            List of IoCs found grouped by type.

        """
        if cell is None:
            results = self._ioc_extract.extract(src=line)
        else:
            results = self._ioc_extract.extract(src=cell)
        iocs = [(ioc_type, list(ioc_res)) for ioc_type, ioc_res in results.items()]
        args = magic_arguments.parse_argstring(self.ioc, line)
        if args.out is not None:
            self.shell.user_ns[args.out] = results
        return iocs


IPYTHON = get_ipython()
IPYTHON.register_magics(Base64Magic)
IPYTHON.register_magics(IoCExtractMagic)
