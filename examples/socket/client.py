from pubtk.runtk import HPCRunner

client_runner = HPCRunner()

data = client_runner.socketfile

print(client_runner.socketfile)

print("attempting connection")

client_runner.connect()
print("connected")
client_runner.send(data)

client_runner.close()

