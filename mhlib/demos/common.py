"""Some functions common for all demo applications."""

import logging
from pkg_resources import resource_filename

from mhlib.settings import parse_settings, settings, get_settings_parser, get_settings_as_str
from mhlib.log import init_logger
from mhlib.scheduler import Method
from mhlib.gvns import GVNS
from mhlib.alns import ALNS
from mhlib.par_alns import ParallelALNS
from mhlib.pbig import PBIG
from mhlib.ssga import SSGA


data_dir = resource_filename("mhlib", "demos/data/")


def run_optimization(problem_name: str, Instance, Solution, default_inst_file: str, own_settings=None):
    """Run optimization algorithm given by parameter alg on given problem instance."""
    parser = get_settings_parser()
    parser.add("--alg", type=str, default='gvns', help='optimization algorithm to be used (gvns, alns, parallel_alns)')
    parser.add("--inst_file", type=str, default=default_inst_file,
               help='problem instance file')
    parser.add("--meths_ch", type=int, default=1,
               help='number of construction heuristics to be used')
    parser.add("--meths_li", type=int, default=1,
               help='number of local improvement methods to be used')
    parser.add("--meths_sh", type=int, default=5,
               help='number of shaking methods to be used')
    parser.add("--meths_de", type=int, default=3,
               help='number of destroy methods to be used')
    parser.add("--meths_re", type=int, default=3,
               help='number of repair methods to be used')
    # parser.set_defaults(seed=3)

    parse_settings()
    init_logger()
    logger = logging.getLogger("mhlib")
    logger.info(f"mhlib demo for solving {problem_name}")
    logger.info(get_settings_as_str())
    instance = Instance(settings.inst_file)
    logger.info(f"{problem_name} instance read:\n" + str(instance))
    solution = Solution(instance)
    # solution.initialize(0)

    logger.info(f"Solution: {solution}, obj={solution.obj()}\n")

    if settings.alg == 'gvns':
        alg = GVNS(solution,
                   [Method(f"ch{i}", Solution.construct, i) for i in range(settings.meths_ch)],
                   [Method(f"li{i}", Solution.local_improve, i) for i in range(1, settings.meths_li + 1)],
                   [Method(f"sh{i}", Solution.shaking, i) for i in range(1, settings.meths_sh + 1)],
                   own_settings)
    elif settings.alg == 'alns':
        alg = ALNS(solution,
                   [Method(f"ch{i}", Solution.construct, i) for i in range(settings.meths_ch)],
                   [Method(f"de{i}", Solution.destroy, i) for i in range(1, settings.meths_de + 1)],
                   [Method(f"re{i}", Solution.repair, i) for i in range(1, settings.meths_re + 1)],
                   own_settings)
    elif settings.alg == 'pbig':
        alg = PBIG(solution,
                   [Method(f"ch{i}", Solution.construct, i) for i in range(settings.meths_ch)],
                   [Method(f"li{i}", Solution.local_improve, i) for i in range(1, settings.meths_li + 1)] +
                   [Method(f"sh{i}", Solution.shaking, i) for i in range(1, settings.meths_sh + 1)],
                   own_settings)
    elif settings.alg == 'par_alns':
        alg = ParallelALNS(solution,
                           [Method(f"ch{i}", Solution.construct, i) for i in range(settings.meths_ch)],
                           [Method(f"de{i}", Solution.destroy, i) for i in range(1, settings.meths_de + 1)],
                           [Method(f"re{i}", Solution.repair, i) for i in range(1, settings.meths_re + 1)],
                           own_settings)
    elif settings.alg == 'ssga':
        alg = SSGA(solution,
                   [Method(f"ch{i}", Solution.construct, i) for i in range(settings.meths_ch)],
                   Solution.crossover,
                   Method(f"mu", Solution.shaking, 1),
                   Method(f"ls", Solution.local_improve, 1),
                   own_settings)
    else:
        raise ValueError('Invalid optimization algorithm selected (settings.alg): ', settings.alg)

    alg.run()
    logger.info("")
    alg.method_statistics()
    alg.main_results()
