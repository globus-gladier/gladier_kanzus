from gladier import GladierBaseClient


class KanzusClient(GladierBaseClient):
    gladier_tools = [
    ]
    flow_definition = ##TODO change that to the original flow ryan was using
##



##Arg Parsing
def parse_args():
    parser = argparse.ArgumentParser()
    ##
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger = logging.getLogger()
    if args.verbose:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)

    kanzus_cli = Kanzus_Client()
    kanzus_cli.get_input()

    # if args.dry_run:
    #     print(json.dumps(flow_input, indent=2))
    #     sys.exit()
    # else:
    #     corr_flow = corr_cli.run_flow(flow_input=flow_input)
    #     corr_cli.check_flow(corr_flow['action_id'])


    buckets = ['/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00256.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00512.cbf',
               '/net/data/idsbc/idstaff/S8/nsp10nsp16/A/Akaroa5_6_00768.cbf']
    res = create_flow_input(buckets)
    from pprint import pprint
    pprint(res)
