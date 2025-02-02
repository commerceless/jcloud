from .base import set_base_parser


def set_remove_parser(parser=None):
    if not parser:
        parser = set_base_parser()

    parser.add_argument(
        '--phase',
        help='The phase to filter flows on for removal',
        type=str,
        choices=['Pending', 'Starting', 'Updating', 'Serving', 'Paused', 'Failed'],
    )

    parser.add_argument(
        'flows',
        nargs="*",
        help='The string ID of a flow for single removal, '
        'or a list of space seperated string IDs for multiple removal, '
        'or string \'all\' for deleting ALL SERVING flows.',
    )
    return parser
