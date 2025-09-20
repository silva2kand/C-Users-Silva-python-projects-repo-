#!/usr/bin/env python3
"""
Legion CLI - Command Line Interface for the AI Agent Swarm
"""
import argparse
import asyncio
import sys
from pathlib import Path
import yaml
import json

# Add the legion package to the path
sys.path.insert(0, str(Path(__file__).parent))

from legion.core import LegionCore


def load_config():
    """Loads configuration from default and user files."""
    legion_dir = Path(__file__).parent
    default_config = legion_dir / 'config' / 'default.yaml'
    user_config = Path.home() / '.legion' / 'config.yaml'

    # Load default config
    if default_config.exists():
        with open(default_config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Create default config if it doesn't exist
        config = get_default_config()

    # Override with user config if it exists
    if user_config.exists():
        with open(user_config, 'r') as f:
            user_config_data = yaml.safe_load(f)
            config.update(user_config_data)

    return config


def get_default_config():
    """Returns default configuration"""
    return {
        'models': {
            'ollama': {
                'enabled': True,
                'host': 'http://localhost:11434',
                'model': 'codellama:7b'
            },
            'openai': {
                'enabled': False,
                'model': 'gpt-4',
                'api_key': ''
            },
            'openrouter': {
                'enabled': False,
                'model': 'anthropic/claude-3-haiku',
                'api_key': ''
            }
        },
        'journal': {
            'enabled': True,
            'path': './.legion/logs'
        },
        'narration': {
            'enabled': False,
            'language': 'en'
        },
        'context_engine': {
            'vector_db': 'chromadb',
            'index_all_files': True,
            'max_context_length': 4000
        }
    }


def setup_project(project_root: Path):
    """Initialize Legion in a project directory"""
    legion_dir = project_root / '.legion'
    legion_dir.mkdir(exist_ok=True)

    # Create user profile
    user_profile = legion_dir / 'user_profile.yaml'
    if not user_profile.exists():
        default_profile = {
            'coding_style': 'concise',
            'language': 'en',
            'experience_level': 'intermediate',
            'preferred_languages': ['python', 'javascript'],
            'auto_apply_suggestions': False
        }
        with open(user_profile, 'w') as f:
            yaml.dump(default_profile, f)

    # Create logs directory
    logs_dir = legion_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)

    print(f"✅ Legion initialized in {project_root}")


async def main():
    parser = argparse.ArgumentParser(
        description='🧠 Legion: AI Code Agent Swarm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  legion complete_code --file ./src/app.py --code "def get_user(id):"
  legion refactor_code --file ./utils/helpers.py
  legion explain_code --file ./config/settings.py --line 15
  legion find_bug --file ./app.py
  legion init  # Initialize Legion in current project
        """
    )

    parser.add_argument('task', nargs='?', help='The task to perform')
    parser.add_argument('--file', '-f', help='File to operate on')
    parser.add_argument('--code', '-c', help='Current code snippet')
    parser.add_argument('--line', '-l', type=int, help='Specific line number')
    parser.add_argument('--project', '-p', help='Project root directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--auto-apply', '-a', action='store_true', help='Auto-apply suggestions')

    args = parser.parse_args()

    # Handle special commands
    if args.task == 'init':
        project_root = Path(args.project) if args.project else Path.cwd()
        setup_project(project_root)
        return

    if not args.task:
        parser.print_help()
        return

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return

    # Determine project root
    project_root = Path(args.project) if args.project else Path.cwd()

    if not project_root.exists():
        print(f"❌ Project root does not exist: {project_root}")
        return

    # Initialize Legion
    try:
        legion = LegionCore(str(project_root), config)
    except Exception as e:
        print(f"❌ Failed to initialize Legion: {e}")
        return

    # Prepare initial context
    context = {
        'file_path': args.file,
        'line_number': args.line,
        'auto_apply': args.auto_apply,
        'verbose': args.verbose
    }

    # Read code from file or argument
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            try:
                context['code'] = file_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"❌ Failed to read file {args.file}: {e}")
                return
        else:
            print(f"❌ File does not exist: {args.file}")
            return
    elif args.code:
        context['code'] = args.code
    else:
        print("❌ Either --file or --code must be provided")
        return

    # Add task description
    context['task_description'] = args.task

    # Execute the task
    try:
        print(f"🚀 Executing task: {args.task}")
        if args.verbose:
            print(f"📁 Project: {project_root}")
            print(f"📄 File: {args.file}")
            print(f"📝 Code length: {len(context.get('code', ''))} characters")

        result = await legion.request(args.task, context)

        # Display results
        if result.get('action') == 'error':
            print(f"❌ Error: {result.get('output', 'Unknown error')}")
        else:
            print("✅ Task completed successfully!")
            if args.verbose:
                print("\n📊 Results:")
                print(json.dumps(result, indent=2))
            else:
                output = result.get('output', '')
                if isinstance(output, str) and len(output) > 200:
                    print(f"📝 Output: {output[:200]}...")
                else:
                    print(f"📝 Output: {output}")

    except Exception as e:
        print(f"❌ Task execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())