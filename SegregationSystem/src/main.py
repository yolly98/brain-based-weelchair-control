from src.segregation_system import SegregationSystem
import utility.logging as log

if __name__ == '__main__':

    segregation_system = SegregationSystem()
    try:
        segregation_system.run()
    except KeyboardInterrupt:
        log.warning("Segregation App terminated")
        exit(0)



