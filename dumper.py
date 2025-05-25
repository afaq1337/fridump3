import os
import logging
import threading

class TimeoutException(Exception): pass

def call_with_timeout(func, timeout=5, *args, **kwargs):
    result = [TimeoutException("Timeout")]
    def wrapper():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            result[0] = e

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join(timeout)
    if isinstance(result[0], Exception):
        raise result[0]
    return result[0]

# Reading bytes from session and saving it to a file


def dump_to_file(agent, base, size, error, directory):
    try:
        filename = str(base) + '_dump.data'
        dump = call_with_timeout(agent.read_memory, 1.5, base, size)
        f = open(os.path.join(directory, filename), 'wb')
        f.write(dump)
        f.close()
        return error
    except TimeoutException:
        logging.warning(f"Timeout reading memory at {base}, skipping.")
        return error
    except Exception as e:
        logging.debug(str(e))
        print("Oops, memory access violation!")
        return error

# Read bytes that are bigger than the max_size value, split them into chunks and save them to a file

def splitter(agent,base,size,max_size,error,directory):
        times = size//max_size
        diff = size % max_size
        if diff == 0:
            logging.debug("Number of chunks:"+str(times+1))
        else:
            logging.debug("Number of chunks:"+str(times))
        global cur_base
        cur_base = int(base,0)

        for time in range(times):
                # logging.debug("Save bytes: "+str(cur_base)+" till "+str(hex(cur_base+max_size)))
                dump_to_file(agent, cur_base, max_size, error, directory)
                cur_base = cur_base + max_size

        if diff != 0:
            # logging.debug("Save bytes: "+str(hex(cur_base))+" till "+str(hex(cur_base+diff)))
            dump_to_file(agent, cur_base, diff, error, directory)
