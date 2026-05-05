# IT Help Desk Ticketing System

## Overview

The IT Help Desk Ticketing System is a web-based application designed to manage and streamline IT support requests within an organization. It replaces unstructured communication methods such as emails and phone calls with a centralized, trackable, and efficient ticket-based workflow.

## Problem Statement

In many organizations, IT issues are reported through informal channels, leading to:

* Lack of tracking of requests
* Delayed resolution due to unclear ownership
* No accountability or performance visibility
* Absence of analytical insights

This system addresses these challenges by introducing structured ticket management.

## Objectives

* Provide a centralized system for raising and tracking IT issues
* Enable priority-based ticket handling
* Improve accountability through technician assignment
* Generate reports for monitoring performance
* Reduce resolution time using structured workflows and SLA

## Features

* Ticket creation with unique ID generation
* Automatic priority detection based on issue description
* Role-based access for Employee, Technician, and Manager
* Ticket status tracking (Created, Assigned, In Progress, Resolved)
* SLA-based escalation handling
* Dashboard with ticket overview and performance insights

## System Roles

* Employee: Raises tickets and tracks status
* IT Technician: Views and resolves assigned tickets
* IT Manager: Assigns tickets and monitors system performance

## Technology Stack

* Programming Language: Python
* Framework: Streamlit
* Data Storage: JSON (lightweight storage for prototype)
* Deployment: Streamlit Community Cloud

## System Architecture

The system follows a single-tier architecture where the user interface, application logic, and data handling are integrated within a single application. This simplifies development but has limitations in scalability for large-scale systems.

## Workflow

1. Employee submits an issue through the system
2. Ticket is generated with a unique ID and assigned priority
3. Manager assigns the ticket to a technician
4. Technician updates status and provides resolution
5. System tracks progress and generates reports

## SDLC Methodology

The project follows the Waterfall Model:

* Planning: Problem identification
* Analysis: Requirement gathering
* Design: DFD and ER diagram creation
* Implementation: Development using Python and Streamlit
* Testing: Functional validation
* Deployment: Hosting on cloud

## Limitations

* Uses JSON instead of a relational database
* Limited scalability for multiple concurrent users
* Basic security without authentication system
* Manual role selection

## Future Enhancements

* Integration with relational database (MySQL/PostgreSQL)
* User authentication and authorization system
* Automatic ticket assignment based on workload
* Email notifications and alerts
* Advanced analytics and reporting
* Improved UI/UX and scalability

## Conclusion

This project demonstrates the application of System Analysis and Design principles to solve a real-world problem. It provides a structured, efficient, and scalable approach to IT support management while covering the complete system development lifecycle.

---
