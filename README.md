# Game-Finder
D&D player finder Djano web application.

Allows users to post requests to play a game, with the option to DM/host and
a distance they are willing to travel if someone else hosts.
Once a group of players exists where a DM/host has enough other players willing to
travel to their location a notification is sent to the DM with everyone's email
address to begin coordinating the game.

Requirements:
Uses the PostGIS extension for PostgreSQL to support distance searches.
Uses the GeoPy library for address to geographical coordinate conversion.
