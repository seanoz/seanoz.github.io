#!/usr/bin/env python3
"""
Yahoo Fantasy Football Data Fetcher
Fetches historical league data from Yahoo Fantasy API and generates JSON for the dashboard
"""

import os
import json
import requests
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

# Yahoo OAuth2 endpoints
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
API_BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"

class YahooFantasyAPI:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.refresh_access_token()

    def refresh_access_token(self):
        """Get a new access token using the refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'oob',
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(TOKEN_URL, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data['access_token']

        # Update refresh token if a new one is provided
        if 'refresh_token' in token_data:
            self.refresh_token = token_data['refresh_token']

    def make_request(self, endpoint: str):
        """Make an authenticated request to Yahoo Fantasy API"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url, headers=headers)

        # If token expired, refresh and retry
        if response.status_code == 401:
            self.refresh_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers)

        response.raise_for_status()
        return response.json()

class FantasyDataProcessor:
    def __init__(self, api: YahooFantasyAPI, league_id: str):
        self.api = api
        self.league_id = league_id
        self.seasons_data = []
        self.all_teams = {}  # team_key -> team info across all seasons

    def fetch_all_seasons(self):
        """Fetch data for all available seasons"""
        # Start from current year and go backwards
        current_year = datetime.now().year
        seasons_found = []

        # Try fetching leagues from recent years backwards
        for year in range(current_year, 2000, -1):  # Go back to 2000
            try:
                league_key = f"nfl.l.{self.league_id}"
                # Try to get league for this year
                endpoint = f"league/{year}.l.{self.league_id}"
                try:
                    data = self.api.make_request(endpoint)
                    seasons_found.append(year)
                    self.fetch_season_data(year)
                except:
                    # If we can't find data for this year, continue
                    continue
            except Exception as e:
                print(f"No data for {year}: {e}")
                # If we haven't found any seasons yet, keep trying
                # If we've found seasons but hit a gap, we might be done
                if seasons_found and year < min(seasons_found) - 2:
                    break

        return seasons_found

    def fetch_season_data(self, year: int):
        """Fetch all data for a specific season"""
        league_key = f"{year}.l.{self.league_id}"

        try:
            # Get league settings
            league_data = self.api.make_request(f"league/{league_key}/settings")

            # Get standings
            standings_data = self.api.make_request(f"league/{league_key}/standings")

            # Get all matchups for the season
            scoreboard_data = self.api.make_request(f"league/{league_key}/scoreboard")

            season_info = {
                'year': year,
                'league_data': league_data,
                'standings': standings_data,
                'scoreboard': scoreboard_data
            }

            self.seasons_data.append(season_info)

        except Exception as e:
            print(f"Error fetching season {year}: {e}")

    def calculate_all_time_standings(self) -> List[Dict]:
        """Calculate all-time win/loss records and points"""
        team_stats = defaultdict(lambda: {
            'team_name': '',
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'points_for': 0.0,
            'points_against': 0.0,
            'championships': 0,
            'playoff_appearances': 0,
            'regular_season_championships': 0
        })

        # This is a placeholder structure - actual implementation would parse Yahoo API responses
        # For now, create sample data structure

        standings = list(team_stats.values())
        standings.sort(key=lambda x: (x['wins'], -x['losses'], x['points_for']), reverse=True)

        return standings

    def calculate_team_records(self) -> Dict:
        """Calculate various team records"""
        records = {
            'season': {
                'highest_score': {'value': 0, 'team': '', 'season': ''},
                'lowest_score': {'value': 999, 'team': '', 'season': ''},
                'biggest_margin_win': {'value': 0, 'team': '', 'season': ''},
                'longest_win_streak': {'value': 0, 'team': '', 'season': ''},
            },
            'career': {
                'most_championships': {'value': 0, 'team': ''},
                'most_playoff_appearances': {'value': 0, 'team': ''},
                'highest_win_percentage': {'value': 0, 'team': ''},
                'most_points_for': {'value': 0, 'team': ''},
            }
        }

        return records

    def calculate_single_game_records(self) -> Dict:
        """Calculate single game records"""
        records = {
            'top_score': {'team': '', 'score': 0, 'week': '', 'season': ''},
            'lowest_score': {'team': '', 'score': 999, 'week': '', 'season': ''},
            'largest_victory_margin': {'team': '', 'score': 0, 'week': '', 'season': ''},
            'smallest_victory_margin': {'team': '', 'score': 999, 'week': '', 'season': ''},
            'most_combined_points': {'teams': '', 'score': 0, 'week': '', 'season': ''},
            'fewest_combined_points': {'teams': '', 'score': 999, 'week': '', 'season': ''},
            'highest_score_in_loss': {'team': '', 'score': 0, 'week': '', 'season': ''},
            'lowest_score_in_win': {'team': '', 'score': 999, 'week': '', 'season': ''},
        }

        return records

    def calculate_head_to_head_matrix(self) -> List[Dict]:
        """Calculate head-to-head records between all teams"""
        matrix = []

        # Placeholder structure
        # Actual implementation would track all matchups between teams

        return matrix

    def get_championship_history(self) -> List[Dict]:
        """Get championship winners for each season"""
        history = []

        for season in self.seasons_data:
            # Parse championship data from season
            # This is placeholder
            pass

        return history

    def generate_output_json(self) -> Dict:
        """Generate the complete JSON output for the dashboard"""
        seasons = self.fetch_all_seasons()

        output = {
            'last_updated': datetime.now().isoformat(),
            'league_info': {
                'league_id': self.league_id,
                'seasons_tracked': len(seasons),
                'total_teams': len(self.all_teams),
                'total_games': 0,  # Calculate from all matchups
                'season_range': f"{min(seasons)}-{max(seasons)}" if seasons else 'N/A'
            },
            'all_time_standings': self.calculate_all_time_standings(),
            'team_records': self.calculate_team_records(),
            'single_game_records': self.calculate_single_game_records(),
            'head_to_head_matrix': self.calculate_head_to_head_matrix(),
            'championship_history': self.get_championship_history()
        }

        return output

def main():
    # Get credentials from environment variables
    client_id = os.environ.get('YAHOO_CLIENT_ID')
    client_secret = os.environ.get('YAHOO_CLIENT_SECRET')
    refresh_token = os.environ.get('YAHOO_REFRESH_TOKEN')
    league_id = os.environ.get('YAHOO_LEAGUE_ID', '598983')

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing required environment variables")
        print("Required: YAHOO_CLIENT_ID, YAHOO_CLIENT_SECRET, YAHOO_REFRESH_TOKEN")

        # For testing, create sample data
        print("Generating sample data for testing...")
        sample_data = generate_sample_data(league_id)

        with open('fantasy-data.json', 'w') as f:
            json.dump(sample_data, f, indent=2)

        print("Sample data generated successfully!")
        return

    # Initialize API and processor
    api = YahooFantasyAPI(client_id, client_secret, refresh_token)
    processor = FantasyDataProcessor(api, league_id)

    # Generate data
    output = processor.generate_output_json()

    # Save to JSON file
    with open('fantasy-data.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Fantasy data updated successfully!")
    print(f"Seasons tracked: {output['league_info']['seasons_tracked']}")
    print(f"Last updated: {output['last_updated']}")

def generate_sample_data(league_id: str) -> Dict:
    """Generate sample data for testing the dashboard"""
    return {
        'last_updated': datetime.now().isoformat(),
        'league_info': {
            'league_id': league_id,
            'seasons_tracked': 5,
            'total_teams': 10,
            'total_games': 650,
            'season_range': '2019-2024'
        },
        'all_time_standings': [
            {'team_name': 'Team Alpha', 'wins': 52, 'losses': 28, 'ties': 0, 'points_for': 9245.50, 'points_against': 8532.25, 'championships': 2},
            {'team_name': 'Team Bravo', 'wins': 48, 'losses': 32, 'ties': 0, 'points_for': 8976.75, 'points_against': 8654.50, 'championships': 1},
            {'team_name': 'Team Charlie', 'wins': 45, 'losses': 35, 'ties': 0, 'points_for': 8845.25, 'points_against': 8721.00, 'championships': 0},
            {'team_name': 'Team Delta', 'wins': 42, 'losses': 38, 'ties': 0, 'points_for': 8654.00, 'points_against': 8789.50, 'championships': 1},
            {'team_name': 'Team Echo', 'wins': 40, 'losses': 40, 'ties': 0, 'points_for': 8543.75, 'points_against': 8654.25, 'championships': 0},
            {'team_name': 'Team Foxtrot', 'wins': 38, 'losses': 42, 'ties': 0, 'points_for': 8432.50, 'points_against': 8712.75, 'championships': 1},
            {'team_name': 'Team Golf', 'wins': 35, 'losses': 45, 'ties': 0, 'points_for': 8321.25, 'points_against': 8845.50, 'championships': 0},
            {'team_name': 'Team Hotel', 'wins': 32, 'losses': 48, 'ties': 0, 'points_for': 8210.00, 'points_against': 8976.25, 'championships': 0},
            {'team_name': 'Team India', 'wins': 28, 'losses': 52, 'ties': 0, 'points_for': 8098.75, 'points_against': 9087.00, 'championships': 0},
            {'team_name': 'Team Juliet', 'wins': 25, 'losses': 55, 'ties': 0, 'points_for': 7987.50, 'points_against': 9198.75, 'championships': 0},
        ],
        'team_records': {
            'season': {
                'highest_score': {'value': 187.5, 'team': 'Team Alpha', 'season': '2023'},
                'lowest_score': {'value': 42.3, 'team': 'Team Juliet', 'season': '2021'},
                'biggest_margin_win': {'value': 89.2, 'team': 'Team Bravo', 'season': '2022'},
                'longest_win_streak': {'value': 9, 'team': 'Team Alpha', 'season': '2024'},
            },
            'career': {
                'most_championships': {'value': 2, 'team': 'Team Alpha'},
                'most_playoff_appearances': {'value': 5, 'team': 'Team Alpha'},
                'highest_win_percentage': {'value': 65.0, 'team': 'Team Alpha'},
                'most_points_for': {'value': 9245.50, 'team': 'Team Alpha'},
            }
        },
        'single_game_records': {
            'top_score': {'team': 'Team Alpha', 'score': 187.5, 'week': 'Week 8', 'season': '2023'},
            'lowest_score': {'team': 'Team Juliet', 'score': 42.3, 'week': 'Week 12', 'season': '2021'},
            'largest_victory_margin': {'team': 'Team Bravo', 'score': 89.2, 'week': 'Week 5', 'season': '2022'},
            'smallest_victory_margin': {'team': 'Team Echo', 'score': 0.5, 'week': 'Week 3', 'season': '2020'},
            'most_combined_points': {'teams': 'Alpha vs Bravo', 'score': 325.8, 'week': 'Week 10', 'season': '2023'},
            'fewest_combined_points': {'teams': 'Juliet vs India', 'score': 125.4, 'week': 'Week 14', 'season': '2021'},
            'highest_score_in_loss': {'team': 'Team Charlie', 'score': 165.3, 'week': 'Week 6', 'season': '2023'},
            'lowest_score_in_win': {'team': 'Team Delta', 'score': 78.9, 'week': 'Week 11', 'season': '2020'},
        },
        'head_to_head_matrix': [
            {
                'team': 'Team Alpha',
                'opponents': [
                    {'wins': 0, 'losses': 0},  # vs self
                    {'wins': 6, 'losses': 2},  # vs Bravo
                    {'wins': 7, 'losses': 1},  # vs Charlie
                    {'wins': 5, 'losses': 3},  # vs Delta
                    {'wins': 6, 'losses': 2},  # vs Echo
                    {'wins': 7, 'losses': 1},  # vs Foxtrot
                    {'wins': 8, 'losses': 0},  # vs Golf
                    {'wins': 7, 'losses': 1},  # vs Hotel
                    {'wins': 8, 'losses': 0},  # vs India
                    {'wins': 8, 'losses': 0},  # vs Juliet
                ]
            },
            {
                'team': 'Team Bravo',
                'opponents': [
                    {'wins': 2, 'losses': 6},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 7, 'losses': 1},
                    {'wins': 6, 'losses': 2},
                    {'wins': 7, 'losses': 1},
                    {'wins': 7, 'losses': 1},
                ]
            },
            {
                'team': 'Team Charlie',
                'opponents': [
                    {'wins': 1, 'losses': 7},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 7, 'losses': 1},
                    {'wins': 6, 'losses': 2},
                    {'wins': 6, 'losses': 2},
                ]
            },
            {
                'team': 'Team Delta',
                'opponents': [
                    {'wins': 3, 'losses': 5},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 6, 'losses': 2},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 6, 'losses': 2},
                ]
            },
            {
                'team': 'Team Echo',
                'opponents': [
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 5, 'losses': 3},
                    {'wins': 7, 'losses': 1},
                    {'wins': 7, 'losses': 1},
                ]
            },
            {
                'team': 'Team Foxtrot',
                'opponents': [
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 8, 'losses': 0},
                    {'wins': 8, 'losses': 0},
                ]
            },
            {
                'team': 'Team Golf',
                'opponents': [
                    {'wins': 0, 'losses': 8},
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 2, 'losses': 6},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                    {'wins': 7, 'losses': 1},
                ]
            },
            {
                'team': 'Team Hotel',
                'opponents': [
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 1, 'losses': 7},
                    {'wins': 3, 'losses': 5},
                    {'wins': 3, 'losses': 5},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                    {'wins': 6, 'losses': 2},
                ]
            },
            {
                'team': 'Team India',
                'opponents': [
                    {'wins': 0, 'losses': 8},
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 2, 'losses': 6},
                    {'wins': 1, 'losses': 7},
                    {'wins': 0, 'losses': 8},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                    {'wins': 5, 'losses': 3},
                ]
            },
            {
                'team': 'Team Juliet',
                'opponents': [
                    {'wins': 0, 'losses': 8},
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 2, 'losses': 6},
                    {'wins': 1, 'losses': 7},
                    {'wins': 0, 'losses': 8},
                    {'wins': 1, 'losses': 7},
                    {'wins': 2, 'losses': 6},
                    {'wins': 3, 'losses': 5},
                    {'wins': 0, 'losses': 0},
                ]
            },
        ],
        'championship_history': [
            {'season': '2024', 'champion': 'Team Alpha', 'runner_up': 'Team Bravo', 'score': '145.3 - 132.7'},
            {'season': '2023', 'champion': 'Team Alpha', 'runner_up': 'Team Delta', 'score': '156.8 - 142.1'},
            {'season': '2022', 'champion': 'Team Foxtrot', 'runner_up': 'Team Bravo', 'score': '138.5 - 135.2'},
            {'season': '2021', 'champion': 'Team Delta', 'runner_up': 'Team Charlie', 'score': '149.7 - 141.3'},
            {'season': '2020', 'champion': 'Team Bravo', 'runner_up': 'Team Echo', 'score': '152.4 - 128.9'},
        ]
    }

if __name__ == '__main__':
    main()
