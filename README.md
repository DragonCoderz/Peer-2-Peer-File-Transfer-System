## P2P File Transfer System Project

This project implements a peer-to-peer file sharing system. The system consists of two components:

* A **P2PClient** that can download files from other P2PClients.
* A **P2PTracker** that keeps track of which P2PClients have which files.

## How to Use

To use the system, you first need to start the P2PTracker. The P2PTracker can be started with the following command:

```
python3 p2ptracker.py
```

Once the P2PTracker is running, you can start P2PClients. To start a P2PClient, you need to specify the folder that contains the files that you want to share. You can also specify the port number that the P2PClient should listen on. For example, to start a P2PClient that shares the files in the `/tmp/files` folder and listens on port 5000, you would use the following command:

```
python3 p2pclient.py -folder /tmp/files -port 5000
```

Once a P2PClient is running, it will connect to the P2PTracker and announce the files that it has. Other P2PClients can then use the P2PTracker to find P2PClients that have the files that they want.

To download a file, a P2PClient will first ask the P2PTracker for a list of P2PClients that have the file. The P2PTracker will then return a list of P2PClients that have the file. The P2PClient will then randomly select one of the P2PClients from the list and connect to it. Once the P2PClient is connected to the other P2PClient, it will request the file. The other P2PClient will then send the file to the P2PClient.

## Assumptions

The following assumptions are made about the system:

* The P2PTracker is always available.
* The P2PClients are always connected to the internet.
* The P2PClients are honest and do not try to cheat the system.

## Limitations

The following limitations are present in the system:

* The system is not secure. Files can be downloaded by anyone who knows the IP address of the P2PClient that is sharing the file.
* The system is not fault-tolerant. If the P2PTracker fails, the system will not be able to find files.
* The system is not scalable to an exceedingly large number of P2PClients. The P2PTracker will eventually become overloaded if too many P2PClients join the system.

## Future Work

The following future work can be done to improve the system:

* Add security to the system to prevent unauthorized users from downloading files.
* Make the system fault-tolerant so that it can continue to function even if the P2PTracker fails.
* Make the system scalable to a huge number of P2PClients.

## Contributing

If you would like to contribute to the project, please follow these steps:

1. Fork the project on GitHub.
2. Create a branch for your changes.
3. Make your changes and commit them to your branch.
4. Push your changes to your fork.
5. Create a pull request to the original project.

## Reporting Bugs

If you find a bug in the project, please report it by creating an issue on GitHub.

## Future Work

The following future work can be done to improve the system:

* Add security to the system to prevent unauthorized users from downloading files.
* Make the system fault-tolerant so that it can continue to function even if the P2PTracker fails.
* Make the system scalable to a large number of P2PClients.
