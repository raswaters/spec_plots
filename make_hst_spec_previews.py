__version__ = '1.0'

"""
.. module:: make_hst_spec_previews
   :synopsis: Given an HST spectrum file name, this script will read in the data and generate preview plots of the spectra.  The plots are generated in different dimensions (large, medium, small, thumbnail) and, depending on the instrument/configuration, are plotted in different formats to maximize readability and usability.
.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
from os import path
import pyfits
import sys
"""These are local modules that are imported."""
import specutils_cos
import specutils_stis


class HSTSpecPrevError(Exception):
    """ This class defines a generic Exception to use for errors raised in MAKE_HST_SPEC_PREVIEWS and specific to this module.  It simply returns the given value when raising the exception, e.g., raise HSTSpecPrevError("Print this string") -> __main__.MyError: 'Print this string.'"""
    def __init__(self, value):
        """
        Initiate the Exception.
        :param value: The string to print on error.
        :type value: str
        """
        self.value = value
    def __str__(self):
        """
        Overrides the str function for this class.
        """
        return "*** MAKE_HST_SPEC_PREVIEWS ERROR: "+repr(self.value)


def setup_args():
    """
    Set up command-line arguments and options.
    :returns: ArgumentParser -- Stores arguments and options.
    """
    parser = argparse.ArgumentParser(description="Create spectroscopic preview plots given an HST spectrum FITS file.")
    parser.add_argument("-f", action="store", type=str, dest="input_file", default=None, help="[Required] Full path to input file (HST spectrum) for which to generate preview plots.  Include the file name in the path.",metavar='input file')
    parser.add_argument("-o", action="store", type=str, dest="output_path", default="", help="[Optional] Full path to output plot files.  Do not inclue file name in path.  Default is the same directory as the input file.",metavar='output path')
    parser.add_argument("-t", action="store", type=str, dest="output_type", default="png", help='[Optional] Specify where plots should be output.  Default = "png".', choices=['png','PNG','screen','SCREEN'], metavar='{png,screen}')
    parser.add_argument("-v", action="store_true", dest="verbose", default=False, help='[Optional] Turn on verbose messages/logging.  Default = "False".')
    return parser


def check_input_options(args):
    """
    Check that input arguments satisfy some minimum requirements.
    :param args: Stores arguments and options.
    :type args: argparse.Namespace object.
    :raises: HSTSpecPrevError
    """

    """Make sure the input file is specified on input (non-empty string), and remove any leading/trailing whitespace.  Catch as an ArgumentsParser error in this case.  If it does exist, check that the input file exists at the time of the command-line parameter checking."""
    if not args.input_file:
        try:
            raise HSTSpecPrevError("File name must be specified.")
        except HSTSpecPrevError as error_string:
            print error_string
            exit(1)
    else:
        args.input_file = args.input_file.strip()
        if not path.isfile(args.input_file):
            try:
                raise HSTSpecPrevError("Input file not found: "+args.input_file)
            except HSTSpecPrevError as error_string:
                print error_string
                exit(1)
    """Make sure the output_type string is trimmed and lowercase."""
    args.output_type = args.output_type.strip().lower()


def get_instrument_name(input_file):
    """
    Determines the instrument name from a FITS file primary header.
    :param input_file: Name of input FITS file.
    :type input_file: str
    :returns: str -- The name of the instrument based on the FITS header keyword, in uppercase with leading/trailing whitespace removed.
    :raises: KeyError
    """
    with pyfits.open(input_file) as hdulist:
        """Make sure the INSTRUME keyword exists in the primary header, otherwise, catch as a PYFITS KeyError in this case."""
        try:
            this_instrument = hdulist[0].header['INSTRUME']
        except KeyError as header_error:
            print "*** MAKE_HST_SPEC_PREVIEWS ERROR: INSTRUME keyword not found in file's primary header: ", input_file
            exit(1)
    return this_instrument.strip().upper()


def make_hst_spec_previews(args):
    """
    Main function in the module.
    :param args:
    :type args: argparse.Namespace object.
    :raises: HSTSpecPrevError
    """
    """Print file name, if verbose is turned on."""
    if args.verbose:
        print "Input file: " + args.input_file

    """Derive output file name from input file name."""
    if args.output_type == "png":
        output_file = path.join(args.output_path,"") + path.basename(args.input_file).split(".fits")[0] + ".png"

    """Print name of output file, if verbose is turned on and not printing to screen."""
    if args.verbose and args.output_type != "screen":
        print "Output file: " + output_file
    elif args.verbose:
        print "Output file: Plotting to screen."

    """Read in the FITS file to determine which instrument it comes from.  Print the name of the instrument found in the header if verbose is turned on."""
    this_instrument = get_instrument_name(args.input_file)
    if args.verbose:
        print "Instrument: " + this_instrument

    """Read in the FITS file to extract wavelengths, fluxes, and flux uncertainties, using the local package appropriate for the instrument used in the input file."""
    if this_instrument == 'COS':
        """Get wavelengths, fluxes, flux uncertainties."""
        spec_tuple = specutils_cos.readspec(args.input_file, args.verbose)
        """Plot spectra preview plots."""
        specutils_cos.plotspec(spec_tuple, args.output_type, output_file)
    elif this_instrument == 'STIS':
        pass
        ## specutils_stis.readspec(args.input_file)
        ## specutils_stis.plotspec()
    else:
        try:
            raise HSTSpecPrevError('"INSTRUME" keyword not understood: ' + this_instrument)
        except HSTSpecPrevError as error_string:
            print error_string
            exit(1)

if __name__ == "__main__":
    """Create ArgumentParser object that holds arguments and options."""
    args = setup_args().parse_args()
    """Check arguments and options."""
    check_input_options(args)
    """Call main function."""
    make_hst_spec_previews(args)
