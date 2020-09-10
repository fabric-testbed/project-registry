# Project Registry

Python (Flask) based ReSTful API service for FABRIC Project Registry management

## Table of Contents

- [About](#about)
- [Usage](#usage) 
  - [Configuration](#config)
  - [Development](#devdeploy)
  - [Production](#proddeploy)
- [API Specification](#apispec)
  - [API Version](#apiversion)
  - [API People](#apipeople)
  - [API Projects](#apiprojects)
- [How to contribute](#contrib)
- [References](#references)

## <a name="about"></a>About

The Project Registry manages FABRIC project creation and membership via a REST API. Recorded project information is a combination of CILogon/COmanage identity and authorization attributes along with internal meta-information about each project. 

Current project membership and roles are maintained and asserted via COmanage. COmanage data represents the roles (groups or permissions) an individual would have within the scope of one or more projects within FABRIC.

The Project Registry also maintains a separate persistent database of projects storing meta-information about each project (e.g. description, purpose) and maintaining a log of actions for each project. COmanage is treated as the single source of "truth" and then augmented by project meta-information which is stored to a separate persistent database. COmanage information is continuously monitored such that no role based project level decision is made without first verifying identity and role via COmanage.

The principal policies guiding the development of the project registry are documented in [fabric-testbed/Authz](https://github.com/fabric-testbed/Authz/tree/master/policies)

The Project Registry is a ReSTful (Representational State Transfer) service implementation using Swagger tooling to define the API specification using the OpenAPI specification.

**What Is OpenAPI?**

OpenAPI Specification (formerly Swagger Specification) is an API description format for REST APIs. An OpenAPI file allows you to describe your entire API, including:

- Available endpoints (/users) and operations on each endpoint (GET /users, POST /users)
- Operation parameters Input and output for each operation
- Authentication methods
- Contact information, license, terms of use and other information.

API specifications can be written in YAML or JSON. The format is easy to learn and readable to both humans and machines. The complete OpenAPI Specification can be found on GitHub: OpenAPI 3.0 Specification

**What Is Swagger?**

Swagger is a set of open-source tools built around the OpenAPI Specification that can help you design, build, document and consume REST APIs. The major Swagger tools include:

- Swagger Editor – browser-based editor where you can write OpenAPI specs.
- Swagger UI – renders OpenAPI specs as interactive API documentation.
- Swagger Codegen – generates server stubs and client libraries from an OpenAPI spec.

## <a name="usage"></a>Usage

A series of scripts have been created to automate common deployment activities and reside within the `scripts` directory.

```console
$ tree -L 1 scripts
scripts
├── README.md                         # Description of each script
├── run-docker-development-server.sh  # Launch docker-compose configuration
├── run-local-database.sh             # Launch local database in Docker
├── run-local-flask-server.sh         # Launch local server using Flask
├── run-local-uwsgi-server.sh         # Launch local server using uWSGI
└── update-swagger-stub.sh            # Format a new python-flask export from swagger
```

Detailed use for each can be found in the [README located in the scripts directory](./scripts)

### <a name="config"></a>Configuration

TODO

### <a name="devdeploy"></a>Development

TODO

### <a name="proddeploy"></a>Production

TODO

## <a name="apispec"></a>API Specification

## Overview

The project registry enforces role based access as defined by the FABRIC COmanage registry.

![overview](images/project-registry.jpg)

### Terminology notes

`PROJECT_ID` - unique project identifier based on [uuid-4](https://docs.python.org/3/library/uuid.html) (e.g. `d505ea38-c409-42e7-833c-24843e8b0aed`)

`PEOPLE_ID` - unique people identifier based on [uuid-4](https://docs.python.org/3/library/uuid.html) (e.g. `ea806951-a22e-4e85-bc70-4ce74b1967b9`)

`CILOGON_ID` - unique person identifier based on CILogon `sub` attribute (e.g. `http://cilogon.org/serverA/users/123456`)

`ROLES` - project related roles that can be one or more of (e.g. project id =`d505ea38-c409-42e7-833c-24843e8b0aed`):

- Facility Operator (e.g. `CO:COU:facility-operator:members:active`)
- Project Lead (e.g. `CO:COU:d505ea38-c409-42e7-833c-24843e8b0aed-pl:members:active`)
- Project Owner (e.g. `CO:COU:d505ea38-c409-42e7-833c-24843e8b0aed-po:members:active`)
- Project Member (e.g. `CO:COU:d505ea38-c409-42e7-833c-24843e8b0aed-pm:members:active`)

`TAGS` - additional attributes applied at the project level and managed by the Facility Operator, for example:

- `peering`
- `cloudconnect`
- `fab-eu`
- `fab-apac`

`NA` - Not Applicable

### <a name="apiversion"></a>Version

The project registry API is versioned

API `version`:

Resource | Action | Input | Output
:--------|:----:|:---:|:---:
`/version` | GET: current API version | NA | Version format

Example: Version format

```json
{
  "gitsha1": "Release SHA as string",
  "version": "Release version as string"
}
```

### <a name="apipeople"></a>People

People are identities as authenticated by CILogon/COmanage and subsetted into groups defined by one or more roles within COmanage. 

People Roles

- **projectLead(principal, facility)**: a project lead can create new projects specific to a given facility. Project Lead may add or remove Project Owners to their project (project they created). Project Lead becomes project owner by default.
- f**acilityOperator(principal, facility)**: a facility operator can create and delete any project and manage owners and members of any project. Facility operator can create slivers in any project subject to project resource constraints.
- **projectOwner(principal, project)**: a project Owner may add or remove project members for the projects they own. Project Owners are also project members.
- **projectMember(principal, project)**: a project Member may create slices assigned to their corresponding project(s). Slice creation requires a membership in a valid project. A project member can provision resources/add slivers into a valid slice subject to resource federation- or aggregate-level resource constraints. A slice may contain slivers created by different project members. A sliver can only be modified or deleted by the project member who created it or by a project owner with one exception: slivers belonging to different project members are automatically allowed to be stitched together as necessary (i.e. if adding a sliver from Alice to a slice requires modifying another sliver already created by Bob, permission is automatically granted assuming Alice and Bob are members of the same project).

API `/people`:

Resource | Action | Input | Output
:--------|:----:|:---:|:---:
`/people` | GET: list of all people | NA | Array of People Short format
`/people/{uuid}` | GET: singular person details | uuid as `PEOPLE_ID` | People Long format

Example: People Long format

```json
{
  "cilogon_id": "CILogon sub claim as string",
  "email": "CILogon email claim as string",
  "eppn": "CILogon eppn claiim as string",
  "name": "CILogon name claim as string",
  "projects": [
    "PROJECT_ID(uuid) as string",
    "PROJECT_ID(uuid) as string"
  ],
  "roles": [
    "COmanage COU as string",
    "COmanage COU as string"
  ],
  "uuid": "PEOPLE_ID(uuid) as string"
}
```

Example: People Short format

```json
{
  "email": "CILogon email claim as string",
  "name": "CILogon name claim as string",
  "uuid": "PEOPLE_ID(uuid) as string"
}
```

### <a name="apiprojects"></a>Projects

Projects in the project registry are the collection of meta-descriptors for the project along with the association of personnel to project roles. There is no context for infrastructure contained within the project registry.

API `/projects`:

Resource | Action | Input | Output
:--------|:----:|:---:|:---:
`/projects` | GET: list of all projects | NA | Array of Project Short format
`/projects/add_members` | PUT: add people to members role | `PROJECT_ID`, array of `PEOPLE_ID` | Project Long format
`/projects/add_owners` | PUT: add people to owners role | `PROJECT_ID`, array of `PEOPLE_ID` | Project Long format
`/projects/add_tags` | PUT: add new tag | `PROJECT_ID`, array of tags | Project Long format
`/projects/create` | POST: create new project | name, description, facility, array of `project_members`, array of `project_owners`, array of `tags` | Project Long format
`/projects/delete` | DELETE: delete existing project | `PROJECT_ID` | Status Code
`/projects/remove_members` | PUT: remove existing people from members role | `PROJECT_ID`, array of `PEOPLE_ID` | Project Long format
`/projects/remove_owners` | PUT: remove existing people from owners role | `PROJECT_ID`, array of `PEOPLE_ID` | Project Long format
`/projects/remove_tags` | PUT: remove existing tag | `PROJECT_ID`, array of tags | Project Long format
`/projects/{uuid}` | GET: singular project details | uuid as `PROJECT_ID` | Project Long format

Example: Project Long format

```json
{
  "description": "Project description as string",
  "facility": "Facility description as string",
  "facility_operators": [
    "PEOPLE_ID(uuid) as string",
    "PEOPLE_ID(uuid) as string"
  ],
  "name": "Project name as string",
  "project_leads": [
    "PEOPLE_ID(uuid) as string",
    "PEOPLE_ID(uuid) as string"
  ],
  "project_members": [
    "PEOPLE_ID(uuid) as string",
    "PEOPLE_ID(uuid) as string"
  ],
  "project_owners": [
    "PEOPLE_ID(uuid) as string",
    "PEOPLE_ID(uuid) as string"
  ],
  "tags": [
    "Tag as string",
    "Tag as string"
  ],
  "uuid": "PROJECT_ID(uuid) as string"
}
```

Example: Project Short format

```json
{
  "description": "Project description as string",
  "facility": "Facility descripton as string",
  "name": "Project name as string",
  "uuid": "PROJECT_ID(uuid) as string"
}
```

## <a name="contrib"></a>How to contribute

TODO

## <a name="references"></a>References

- Swagger: [https://swagger.io](https://swagger.io)
- OpenAPI Specification: [https://swagger.io/docs/specification/about/](https://swagger.io/docs/specification/about/)
- CILogon: [https://www.cilogon.org](https://www.cilogon.org)
- COmanage: [https://www.cilogon.org/comanage](https://www.cilogon.org/comanage)


