#!/usr/bin/env python3
"""
Database Initialization Script
Initialize PostgreSQL database with sample data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.adapters.database.database import init_database, reset_database, get_database_health
from src.adapters.database.repositories.user_repository import UserRepository
from src.adapters.database.repositories.scenario_repository import ScenarioRepository
from src.service.use_cases.user_use_cases import UserUseCases
from src.service.use_cases.scenario_use_cases import ScenarioUseCases
from src.adapters.database.database import db_session
from src.domain.models.user import UserRole
from src.domain.models.scenario import ScenarioDifficulty, ScenarioCategory


def create_default_admin():
    """Create default admin user"""
    print("Creating default admin user...")
    
    with db_session() as session:
        user_repo = UserRepository(session)
        user_use_cases = UserUseCases(user_repo)
        
        try:
            # Check if admin already exists
            admin_user = user_repo.get_by_username('admin')
            if admin_user:
                print("✅ Admin user already exists")
                return
            
            # Create admin user
            result = user_use_cases.register_user(
                username='admin',
                email='admin@banksec-enterprise.com',
                password='AdminPass123!ChangeMe',
                role='admin'
            )
            
            if result['success']:
                print("✅ Admin user created successfully")
                print(f"   Username: admin")
                print(f"   Email: admin@banksec-enterprise.com")
                print(f"   Password: AdminPass123!ChangeMe")
                print("   ⚠️  Please change the default password immediately!")
            else:
                print(f"❌ Failed to create admin user: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")


def create_default_instructor():
    """Create default instructor user"""
    print("Creating default instructor user...")
    
    with db_session() as session:
        user_repo = UserRepository(session)
        user_use_cases = UserUseCases(user_repo)
        
        try:
            # Check if instructor already exists
            instructor_user = user_repo.get_by_username('instructor')
            if instructor_user:
                print("✅ Instructor user already exists")
                return
            
            # Create instructor user
            result = user_use_cases.register_user(
                username='instructor',
                email='instructor@banksec-enterprise.com',
                password='InstructorPass123!ChangeMe',
                role='instructor'
            )
            
            if result['success']:
                print("✅ Instructor user created successfully")
                print(f"   Username: instructor")
                print(f"   Email: instructor@banksec-enterprise.com")
                print(f"   Password: InstructorPass123!ChangeMe")
                print("   ⚠️  Please change the default password immediately!")
            else:
                print(f"❌ Failed to create instructor user: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error creating instructor user: {e}")


def create_sample_scenarios():
    """Create sample training scenarios"""
    print("Creating sample training scenarios...")
    
    with db_session() as session:
        scenario_repo = ScenarioRepository(session)
        attempt_repo = None  # We'll create this later
        scenario_use_cases = ScenarioUseCases(scenario_repo, attempt_repo)
        
        # Get instructor ID
        from src.adapters.database.repositories.user_repository import UserRepository
        user_repo = UserRepository(session)
        instructor = user_repo.get_by_username('instructor')
        instructor_id = instructor.id if instructor else None
        
        # Sample scenarios
        scenarios = [
            {
                'title': 'Phishing Email Detection',
                'description': 'Learn to identify and respond to phishing emails targeting bank employees',
                'difficulty': 'beginner',
                'category': 'phishing',
                'estimated_time': 900,
                'max_score': 100,
                'initial_state': {
                    'attack_pattern': 'credential_theft',
                    'suspicious_count': 3,
                    'attack_source': 'external',
                    'timeframe': '48_hours'
                },
                'correct_actions': [
                    {
                        'type': 'verify_email_source',
                        'points': 15,
                        'feedback': 'Correct! Always verify email sender addresses',
                        'error_feedback': 'Always check the actual email address, not just display name'
                    },
                    {
                        'type': 'report_phishing',
                        'points': 20,
                        'feedback': 'Good! All suspected phishing should be reported immediately',
                        'error_feedback': 'Phishing attempts must be reported to security team'
                    },
                    {
                        'type': 'do_not_click_links',
                        'points': 15,
                        'feedback': 'Correct! Never click links in suspicious emails',
                        'error_feedback': 'Links in suspicious emails can lead to malware'
                    }
                ],
                'attack_indicators': [
                    'suspicious_sender_domain',
                    'urgent_language',
                    'request_for_credentials',
                    'mismatched_urls',
                    'poor_grammar'
                ],
                'educational_content': {
                    'learning_objectives': [
                        'Identify phishing email characteristics',
                        'Understand proper reporting procedures',
                        'Recognize social engineering tactics'
                    ],
                    'resources': [
                        'Phishing Identification Guide',
                        'Incident Response Protocol',
                        'Social Engineering Defense Handbook'
                    ],
                    'real_world_examples': [
                        {
                            'case': '2016 Bangladesh Bank heist',
                            'description': 'Attackers used phishing to gain credentials and attempt $1 billion transfer',
                            'lesson': 'Importance of multi-factor authentication and transaction limits'
                        }
                    ]
                }
            },
            {
                'title': 'Suspicious Transaction Monitoring',
                'description': 'Monitor transaction queue and identify fraudulent transfer patterns',
                'difficulty': 'intermediate',
                'category': 'transaction_monitoring',
                'estimated_time': 1200,
                'max_score': 150,
                'initial_state': {
                    'attack_pattern': 'large_transfer',
                    'suspicious_count': 5,
                    'attack_source': 'compromised_account',
                    'timeframe': '24_hours'
                },
                'correct_actions': [
                    {
                        'type': 'flag_unusual_amount',
                        'points': 20,
                        'feedback': 'Correct! Transactions significantly above normal patterns should be flagged',
                        'error_feedback': 'Large amounts compared to account history require verification'
                    },
                    {
                        'type': 'verify_new_recipient',
                        'points': 15,
                        'feedback': 'Good! First-time recipients require additional verification',
                        'error_feedback': 'New recipients should be verified through secondary channels'
                    },
                    {
                        'type': 'check_velocity',
                        'points': 15,
                        'feedback': 'Correct! Rapid successive transactions indicate potential fraud',
                        'error_feedback': 'Multiple transactions in short timeframes need scrutiny'
                    },
                    {
                        'type': 'place_hold',
                        'points': 25,
                        'feedback': 'Excellent! Placing a hold prevents funds from leaving while investigation occurs',
                        'error_feedback': 'Suspicious transactions should be placed on hold immediately'
                    }
                ],
                'attack_indicators': [
                    'amount_over_threshold',
                    'new_beneficiary',
                    'geographic_anomaly',
                    'time_of_day_anomaly',
                    'device_fingerprint_change'
                ],
                'educational_content': {
                    'learning_objectives': [
                        'Apply transaction monitoring rules',
                        'Identify suspicious patterns',
                        'Execute proper hold procedures'
                    ],
                    'resources': [
                        'Transaction Monitoring Policy',
                        'Fraud Detection Algorithms',
                        'Regulatory Compliance Guide'
                    ],
                    'real_world_examples': [
                        {
                            'case': 'Wire transfer fraud patterns',
                            'description': 'Common patterns in wire transfer fraud',
                            'lesson': 'Importance of velocity checks and recipient verification'
                        }
                    ]
                }
            }
        ]
        
        for scenario_data in scenarios:
            try:
                # Check if scenario already exists
                existing = scenario_repo.get_by_title(scenario_data['title'])
                if existing:
                    print(f"✅ Scenario '{scenario_data['title']}' already exists")
                    continue
                
                # Create scenario
                result = scenario_use_cases.create_scenario(
                    **scenario_data,
                    created_by=instructor_id
                )
                
                if result['success']:
                    print(f"✅ Created scenario: {scenario_data['title']}")
                else:
                    print(f"❌ Failed to create scenario '{scenario_data['title']}': {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error creating scenario '{scenario_data['title']}': {e}")


def check_database_health():
    """Check database health"""
    print("Checking database health...")
    
    health = get_database_health()
    
    print(f"✅ Database connected: {health.get('connected', False)}")
    print(f"📊 Pool status: {health.get('pool_status', {})}")
    
    if health.get('error'):
        print(f"❌ Error: {health['error']}")
        return False
    
    return True


def main():
    """Main initialization function"""
    print("🚀 BankSec Enterprise Database Initialization")
    print("=" * 50)
    
    # Check environment
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    print()
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        init_database()
        print("✅ Database initialized successfully")
        
        # Check health
        if not check_database_health():
            print("❌ Database health check failed")
            return 1
        
        # Create default users
        create_default_admin()
        create_default_instructor()
        
        # Create sample scenarios
        create_sample_scenarios()
        
        print()
        print("🎉 Database initialization completed successfully!")
        print()
        print("📋 Next Steps:")
        print("1. Change default passwords for admin and instructor accounts")
        print("2. Review and customize the sample scenarios")
        print("3. Set up your production environment variables")
        print("4. Run the application: flask run")
        print()
        print("🔐 Security Reminder:")
        print("- Default passwords MUST be changed immediately")
        print("- Use strong, unique passwords in production")
        print("- Enable HTTPS in production environments")
        
        return 0
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())