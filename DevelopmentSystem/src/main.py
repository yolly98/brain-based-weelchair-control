from src.development_system import DevelopmentSystem
from utility.logging import warning

if __name__ == '__main__':
    # start the development system controller
    try:
        DevelopmentSystem().run()
    except KeyboardInterrupt:
        warning('Development System stopped')
        exit(0)
