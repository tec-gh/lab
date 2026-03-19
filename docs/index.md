# lab documentation

This site provides an overview of the repository and links to each project.

## Included projects

### data_connect_viewer

FastAPI server application for:

- receiving JSON from external systems
- storing records in SQLite
- viewing data in a browser
- exporting CSV and JSON
- scheduled SFTP transfer of exported JSON

Documents:

- [Main README](../data_connect_viewer/docs/README.md)
- [Design](../data_connect_viewer/docs/design.md)
- [Deployment](../data_connect_viewer/docs/deployment.md)

### json_export_viewer_client

Flet client application for:

- loading exported JSON files from a folder
- refreshing the display on a configured interval
- running in native GUI or web GUI mode

Documents:

- [Client README](../subprojects/json_export_viewer_client/README.md)
- [Client Build Guide](../subprojects/json_export_viewer_client/BUILD.md)

## Releases

See the GitHub Releases page for downloadable source archives.
