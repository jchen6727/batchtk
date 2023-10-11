from pubtk.runtk import HPCRunner

client_runner = HPCRunner()

data = client_runner.socketfile

#print(client_runner.env)
#print(client_runner.socketfile)
#print(client_runner.client)

client_runner.connect()
client_runner.send(data)

client_runner.close()

