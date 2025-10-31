#!/usr/bin/env python3
"""
Test script for hybrid skills framework
Tests both flat (standard Claude) and nested (enhanced) structures
"""

from pathlib import Path
from backend.agent import SkillsLoader

def test_hybrid_skills():
    """Test that both skill structures work correctly"""

    # Initialize loader
    skills_dir = Path("backend/.claude/skills")
    loader = SkillsLoader(skills_dir=skills_dir)

    print("=" * 60)
    print("HYBRID SKILLS FRAMEWORK TEST")
    print("=" * 60)

    # Test 1: List all skills
    print("\n📋 Test 1: List All Skills")
    print("-" * 60)
    all_skills = loader.list_skills()
    print(f"Found {len(all_skills)} skills:")
    for skill in all_skills:
        structure_type = "FLAT" if skill.is_flat_structure else "NESTED"
        print(f"  [{structure_type:6}] {skill.domain}/{skill.name}")

    # Test 2: Load nested skill (our current structure)
    print("\n📦 Test 2: Load Nested Skill")
    print("-" * 60)
    try:
        skill_path = "change-agent/meeting-minutes-capture"
        metadata = loader.load_skill_metadata(skill_path)
        print(f"✅ Loaded: {metadata.name}")
        print(f"   Domain: {metadata.domain}")
        print(f"   Category: {metadata.category}")
        print(f"   Description: {metadata.description[:80]}...")
        print(f"   Structure: {'Flat' if metadata.is_flat_structure else 'Nested'}")

        # Load instructions
        instructions = loader.load_skill_instructions(skill_path, "capture.md")
        print(f"   Instructions: {len(instructions)} bytes")

        # Load resources
        resources = loader.load_skill_resources(skill_path, "examples.md")
        print(f"   Resources: {len(resources)} bytes")

        # List available files
        instruction_files = loader.list_skill_instructions(skill_path)
        resource_files = loader.list_skill_resources(skill_path)
        print(f"   Available instructions: {instruction_files}")
        print(f"   Available resources: {resource_files}")

    except Exception as e:
        print(f"❌ Error loading nested skill: {e}")

    # Test 3: Filter by domain
    print("\n🔍 Test 3: Filter by Domain")
    print("-" * 60)
    change_skills = loader.list_skills(domain="change-agent")
    print(f"Found {len(change_skills)} change-agent skills:")
    for skill in change_skills:
        print(f"  - {skill.name} ({skill.category})")

    # Test 4: List domains
    print("\n🗂️  Test 4: List Domains")
    print("-" * 60)
    domains = loader.list_domains()
    print(f"Found {len(domains)} domains: {domains}")

    # Test 5: List categories
    print("\n📑 Test 5: List Categories")
    print("-" * 60)
    categories = loader.list_categories()
    print(f"Found {len(categories)} categories: {categories}")

    # Test 6: Get comprehensive skill info
    print("\n📊 Test 6: Get Comprehensive Skill Info")
    print("-" * 60)
    try:
        skill_path = "change-agent/meeting-minutes-capture"
        info = loader.get_skill_info(skill_path)
        print(f"Skill: {info['metadata'].name}")
        print(f"Instructions available: {len(info['instructions'])}")
        print(f"Resources available: {len(info['resources'])}")
        print(f"Content length: {len(info['content'])} bytes")
    except Exception as e:
        print(f"❌ Error getting skill info: {e}")

    print("\n" + "=" * 60)
    print("✅ HYBRID SKILLS FRAMEWORK TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_hybrid_skills()
