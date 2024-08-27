# GeoExplorer

GeoExplorer is a mass scanner project consisting of a client and server component designed to test GeoServer instances for CVE-2024-36401 and log successful exploitations.

## Project Structure

- `client/`: Contains the client-side Python script for sending specially crafted requests to abuse CVE-2024-36401 on GeoServer instances.
- `server/`: Contains the server-side async FastAPI application for logging incoming requests from exploited servers.

## Getting Started

1. Set up the server component by following the instructions in `server/README.md`.
2. Use the client component as described in `client/README.md`.

## License

This project is licensed under the MIT License.
