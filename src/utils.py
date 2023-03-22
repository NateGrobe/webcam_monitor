class Logging:
    def write_to_log(log):
        with open("logs.txt", "a") as f:
            f.write(log)

    def write_to_stats(stats):
        with open("stats.txt", "a") as f:
            f.write(stats)