from pubtk.runtk import HPCRunner

client_runner = HPCRunner()

data = client_runner.socketip + ':' + client_runner.socketport

#print(data)

print("attempting connection")

client_runner.connect()
#print("connected")
client_runner.send(data)

client_runner.close()

