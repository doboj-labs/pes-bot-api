with open('data.txt') as fp:
    with open('team_data.json', 'w') as json_file:
        json_file.write("[\n")

        for idx, line in enumerate(fp):
            parts = line.split('-')
            write_this = '''{"model": "api.team","pk": %s,"fields": {"name": "%s","real_name": "%s","slug": "%s"}},''' % (
                idx + 1, parts[0], parts[1].strip(), parts[0].replace(" ", "")[:3])

            json_file.writelines(write_this.rstrip())

        json_file.write("\n]")
