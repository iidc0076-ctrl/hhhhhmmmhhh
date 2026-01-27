# Legal Enforcement System
# Comprehensive legal protection and policy enforcement for the trading bot

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import discord

class LegalEnforcement:
    def __init__(self):
        self.violations_log = {}
        self.user_agreements = {}
        self.monitoring_active = True
        
        # Load existing violation records
        try:
            with open('violations.json', 'r') as f:
                self.violations_log = json.load(f)
        except FileNotFoundError:
            self.violations_log = {}
            
        # Load user agreement records
        try:
            with open('user_agreements.json', 'r') as f:
                self.user_agreements = json.load(f)
        except FileNotFoundError:
            self.user_agreements = {}

    def save_records(self):
        """Save violation and agreement records to disk"""
        try:
            with open('violations.json', 'w') as f:
                json.dump(self.violations_log, f, indent=2)
            with open('user_agreements.json', 'w') as f:
                json.dump(self.user_agreements, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save legal records: {e}")

    def check_user_agreement_status(self, user_id: str) -> Dict[str, bool]:
        """Check if user has agreed to all required legal documents"""
        user_str = str(user_id)
        if user_str not in self.user_agreements:
            return {
                'privacy_policy': False,
                'terms_of_service': False,
                'user_conduct': False,
                'all_agreed': False
            }
        
        agreements = self.user_agreements[user_str]
        all_agreed = (
            agreements.get('privacy_policy', False) and
            agreements.get('terms_of_service', False) and
            agreements.get('user_conduct', False)
        )
        
        return {
            'privacy_policy': agreements.get('privacy_policy', False),
            'terms_of_service': agreements.get('terms_of_service', False),
            'user_conduct': agreements.get('user_conduct', False),
            'all_agreed': all_agreed
        }

    def record_user_agreement(self, user_id: str, document_type: str) -> bool:
        """Record user agreement to specific legal document"""
        user_str = str(user_id)
        
        if user_str not in self.user_agreements:
            self.user_agreements[user_str] = {}
            
        self.user_agreements[user_str][document_type] = {
            'agreed': True,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        
        self.save_records()
        return True

    def log_violation(self, user_id: str, violation_type: str, details: str, severity: str = 'medium') -> bool:
        """Log a policy violation"""
        user_str = str(user_id)
        
        if user_str not in self.violations_log:
            self.violations_log[user_str] = []
            
        violation_record = {
            'type': violation_type,
            'details': details,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False
        }
        
        self.violations_log[user_str].append(violation_record)
        self.save_records()
        
        logging.warning(f"Policy violation logged for user {user_id}: {violation_type} - {details}")
        return True

    def get_user_violation_count(self, user_id: str, days: int = 30) -> Dict[str, int]:
        """Get violation count for user within specified days"""
        user_str = str(user_id)
        
        if user_str not in self.violations_log:
            return {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        counts = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for violation in self.violations_log[user_str]:
            violation_date = datetime.fromisoformat(violation['timestamp'])
            if violation_date >= cutoff_date and not violation.get('resolved', False):
                counts['total'] += 1
                severity = violation.get('severity', 'medium')
                if severity in counts:
                    counts[severity] += 1
                    
        return counts

    def should_restrict_user(self, user_id: str) -> Tuple[bool, str]:
        """Determine if user should be restricted based on violations"""
        violations = self.get_user_violation_count(user_id)
        
        # Critical violations result in immediate restriction
        if violations['critical'] > 0:
            return True, "Critical policy violations detected"
            
        # Multiple high severity violations
        if violations['high'] >= 2:
            return True, "Multiple high-severity violations"
            
        # Excessive medium violations
        if violations['medium'] >= 5:
            return True, "Excessive policy violations"
            
        # Total violation threshold
        if violations['total'] >= 10:
            return True, "Pattern of policy violations detected"
            
        return False, ""

    def create_legal_agreement_embed(self, document_type: str) -> discord.Embed:
        """Create Discord embed for legal document agreement"""
        
        if document_type == 'privacy_policy':
            embed = discord.Embed(
                title="📋 Privacy Policy Agreement Required",
                description="To use this service, you must read and agree to our Privacy Policy.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📖 Privacy Policy Summary",
                value="• We collect minimal Discord user data for service operation\n• No personal information is sold or shared commercially\n• You have rights to access, modify, and delete your data\n• We comply with GDPR, CCPA, and other privacy regulations",
                inline=False
            )
            embed.add_field(
                name="🔗 Full Privacy Policy",
                value="The complete Privacy Policy is available in our documentation. By clicking 'Agree', you confirm you have read and accept all terms.",
                inline=False
            )
            
        elif document_type == 'terms_of_service':
            embed = discord.Embed(
                title="⚖️ Terms of Service Agreement Required",
                description="You must agree to our Terms of Service to continue using this service.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="🚫 Key Prohibitions",
                value="• **NO SIGNAL SHARING** outside authorized Discord environment\n• No commercial redistribution of analysis or content\n• No reverse engineering of algorithms or systems\n• Educational use only - not investment advice",
                inline=False
            )
            embed.add_field(
                name="⚠️ Important Disclaimers",
                value="• All trading involves risk of financial loss\n• We provide technical analysis, not investment advice\n• Past performance does not guarantee future results\n• You are responsible for your trading decisions",
                inline=False
            )
            
        elif document_type == 'user_conduct':
            embed = discord.Embed(
                title="👥 User Conduct Policy Agreement Required",
                description="Please review and agree to our community conduct standards.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="🛡️ Community Standards",
                value="• Maintain respectful and professional communication\n• No harassment, spam, or abusive behavior\n• Protect account security and integrity\n• Report violations through proper channels",
                inline=False
            )
            embed.add_field(
                name="⛔ Signal Distribution Rules",
                value="• **STRICTLY FORBIDDEN:** Sharing signals outside this Discord\n• No screenshots, copies, or redistribution allowed\n• Personal use only - commercial use prohibited\n• Violations result in immediate account termination",
                inline=False
            )
            
        embed.set_footer(text="Agreement is required to access service features • Legal protection ensures service sustainability")
        return embed

    def create_violation_warning_embed(self, user_id: str, violation_type: str) -> discord.Embed:
        """Create warning embed for policy violations"""
        violations = self.get_user_violation_count(user_id)
        
        embed = discord.Embed(
            title="⚠️ Policy Violation Warning",
            description=f"A violation of our {violation_type} has been detected and logged.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="📊 Violation Summary",
            value=f"**Total Violations (30 days):** {violations['total']}\n**Critical:** {violations['critical']} | **High:** {violations['high']} | **Medium:** {violations['medium']}",
            inline=False
        )
        
        if violations['total'] >= 3:
            embed.add_field(
                name="🚨 Account Risk",
                value="**WARNING:** Multiple violations detected. Further violations may result in account suspension or termination.",
                inline=False
            )
            
        embed.add_field(
            name="📋 Review Policies",
            value="Please review our Terms of Service, Privacy Policy, and User Conduct Policy to ensure compliance.",
            inline=False
        )
        
        embed.set_footer(text="Violations are permanently logged • Repeated violations result in account restrictions")
        return embed

    async def enforce_signal_sharing_protection(self, message_content: str, user_id: str) -> bool:
        """Monitor for potential signal sharing violations"""
        
        # Keywords that might indicate signal sharing
        sharing_indicators = [
            'screenshot', 'copy', 'share', 'send to', 'forward',
            'telegram', 'whatsapp', 'twitter', 'facebook', 'instagram',
            'sell signal', 'buy signal', 'distribute', 'resell',
            'my group', 'other server', 'outside discord'
        ]
        
        content_lower = message_content.lower()
        
        for indicator in sharing_indicators:
            if indicator in content_lower:
                # Check context to avoid false positives
                if any(word in content_lower for word in ['signal', 'analysis', 'trading', 'bot']):
                    self.log_violation(
                        user_id,
                        'potential_signal_sharing',
                        f"Message contained sharing indicators: {indicator}",
                        'high'
                    )
                    return True
                    
        return False

    def get_enforcement_action(self, user_id: str) -> Dict[str, any]:
        """Determine appropriate enforcement action for user"""
        violations = self.get_user_violation_count(user_id)
        should_restrict, reason = self.should_restrict_user(user_id)
        
        if should_restrict:
            if violations['critical'] > 0:
                return {
                    'action': 'permanent_ban',
                    'reason': 'Critical policy violations',
                    'duration': None
                }
            elif violations['high'] >= 3:
                return {
                    'action': 'extended_suspension',
                    'reason': 'Multiple high-severity violations',
                    'duration': 90  # days
                }
            elif violations['high'] >= 2:
                return {
                    'action': 'temporary_suspension',
                    'reason': 'Repeated high-severity violations',
                    'duration': 30  # days
                }
            else:
                return {
                    'action': 'warning',
                    'reason': reason,
                    'duration': None
                }
        
        return {
            'action': 'none',
            'reason': 'No violations requiring action',
            'duration': None
        }

# Global legal enforcement instance
legal_enforcer = LegalEnforcement()

class LegalAgreementView(discord.ui.View):
    """Discord UI for legal document agreements"""
    
    def __init__(self, document_type: str, user_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.document_type = document_type
        self.user_id = user_id

    @discord.ui.button(label='I Agree', style=discord.ButtonStyle.green, emoji='✅')
    async def agree_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can only agree to your own legal documents.", ephemeral=True)
            return
            
        # Record the agreement
        legal_enforcer.record_user_agreement(str(self.user_id), self.document_type)
        
        # Check if all agreements are complete
        agreement_status = legal_enforcer.check_user_agreement_status(str(self.user_id))
        
        if agreement_status['all_agreed']:
            embed = discord.Embed(
                title="✅ Legal Agreements Complete",
                description="Thank you! You have successfully agreed to all required legal documents and can now access all service features.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📋 Documents Agreed",
                value="• Privacy Policy ✅\n• Terms of Service ✅\n• User Conduct Policy ✅",
                inline=False
            )
            embed.add_field(
                name="🚀 Next Steps",
                value="You can now use all bot commands. Remember to follow our policies to maintain access.",
                inline=False
            )
        else:
            missing = []
            if not agreement_status['privacy_policy']:
                missing.append("Privacy Policy")
            if not agreement_status['terms_of_service']:
                missing.append("Terms of Service")
            if not agreement_status['user_conduct']:
                missing.append("User Conduct Policy")
                
            embed = discord.Embed(
                title="📋 Agreement Recorded",
                description=f"Your agreement to the {self.document_type.replace('_', ' ').title()} has been recorded.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="⏳ Remaining Agreements",
                value=f"Please also agree to: {', '.join(missing)}",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.red, emoji='❌')
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can only respond to your own legal documents.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="❌ Service Access Denied",
            description="You have declined to agree to our legal terms. Access to service features is restricted.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="🚫 Access Limitations",
            value="• Cannot use trading signals or analysis commands\n• Cannot access premium features\n• Limited to basic help and information commands",
            inline=False
        )
        embed.add_field(
            name="🔄 Change Your Mind?",
            value="You can restart the agreement process at any time by using the `/legal` command.",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

def require_legal_agreement(func):
    """Decorator to require legal agreement before command execution"""
    async def wrapper(*args, **kwargs):
        # Extract interaction from args
        interaction = None
        for arg in args:
            if isinstance(arg, discord.Interaction):
                interaction = arg
                break
                
        if not interaction:
            return await func(*args, **kwargs)
            
        user_id = str(interaction.user.id)
        agreement_status = legal_enforcer.check_user_agreement_status(user_id)
        
        if not agreement_status['all_agreed']:
            embed = discord.Embed(
                title="📋 Legal Agreement Required",
                description="You must agree to our legal documents before using this command.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="⚖️ Required Documents",
                value="• Privacy Policy\n• Terms of Service\n• User Conduct Policy",
                inline=False
            )
            embed.add_field(
                name="🚀 Get Started",
                value="Use the `/legal` command to review and agree to our policies.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Check for violations that might restrict access
        should_restrict, reason = legal_enforcer.should_restrict_user(user_id)
        if should_restrict:
            embed = discord.Embed(
                title="🚫 Access Restricted",
                description="Your access to this command has been restricted due to policy violations.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="📋 Reason",
                value=reason,
                inline=False
            )
            embed.add_field(
                name="📞 Appeal Process",
                value="Contact support if you believe this restriction is in error.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Proceed with original function
        return await func(*args, **kwargs)
    
    return wrapper