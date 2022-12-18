import sys
import utils.system

if __name__ == '__main__':
    main = utils.system.System(sys.argv if len(sys.argv) > 1 else None)
    main.logger.debug("Starting window")
    main.create_window()


