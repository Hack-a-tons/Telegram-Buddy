# app/connectors/telegram_bot.py
import asyncio
import logging
from datetime import datetime
from typing import Optional
import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from ..models.message import Message
from ..services.context_manager import ContextManager
from ..services.response_engine import ResponseEngine
from ..agents.buddy_agent import BuddyAgent

logger = logging.getLogger(__name__)

class TelegramBuddy:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        self.context_manager = ContextManager()
        self.response_engine = ResponseEngine()
        self.buddy_agent = None  # Initialize lazily
        self.bot = Bot(token=self.token)
        self.application = Application.builder().token(self.token).build()
        
        # Track which groups the bot is active in
        self.active_groups = set()
        
        self._setup_handlers()
    
    def _get_buddy_agent(self):
        """Lazy initialization of BuddyAgent"""
        if self.buddy_agent is None:
            try:
                self.buddy_agent = BuddyAgent()
            except Exception as e:
                logger.error(f"Failed to initialize BuddyAgent: {e}")
                return None
        return self.buddy_agent
    
    def _setup_handlers(self):
        """Set up telegram command and message handlers"""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("ask", self.ask_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("actions", self.actions_command))
        
        # All non-command messages - this should catch regular text
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Add a catch-all handler for debugging
        self.application.add_handler(
            MessageHandler(filters.ALL, self.debug_handler)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        if chat_type in ['group', 'supergroup']:
            self.active_groups.add(chat_id)
            welcome_msg = (
                "🤖 *Telegram Buddy AI activated!*\n\n"
                "I'm now listening to your conversations and can help with:\n"
                "• Answering questions about your projects\n"
                "• Tracking action items and unresolved tasks\n"
                "• Providing context from previous discussions\n\n"
                "*Commands:*\n"
                "/ask <question> - Ask me anything about your project\n"
                "/status - Show current project status\n"
                "/actions - List unresolved action items\n"
                "/help - Show this help message\n\n"
                "Just mention me (@your_bot_name) or use commands to interact!"
            )
        else:
            welcome_msg = (
                "👋 Hi! I'm Telegram Buddy AI.\n\n"
                "Add me to your developer groups where I can:\n"
                "• Track conversations and context\n"
                "• Answer project-related questions\n"
                "• Detect and remind about action items\n\n"
                "Use /help to see available commands."
            )
        
        await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = (
            "🤖 *Telegram Buddy AI Commands:*\n\n"
            "*/ask <question>* - Ask about your project\n"
            "   Example: `/ask What's the status of the API integration?`\n\n"
            "*/status* - Show current project overview\n\n"
            "*/actions* - List unresolved action items\n\n"
            "*/help* - Show this help message\n\n"
            "*Automatic Features:*\n"
            "• I listen to all group messages\n"
            "• I track conversation context\n"
            "• I detect action items and tasks\n"
            "• I can answer questions about previous discussions\n\n"
            "*Just mention me* @BuddianBot *in your message to get my attention!*"
        )
        await update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a question after /ask\n"
                "Example: `/ask What tasks are still pending?`"
            )
            return
        
        question = " ".join(context.args)
        chat_id = str(update.effective_chat.id)
        
        # Get buddy agent
        buddy = self._get_buddy_agent()
        if not buddy:
            await update.message.reply_text(
                "❌ Sorry, I'm having trouble initializing my AI capabilities. Please try again later."
            )
            return
        
        try:
            # Get context for this chat
            chat_context = self.context_manager.get_context(chat_id)
            
            # Create QueryRequest object as expected by BuddyAgent
            from ..models.context import QueryRequest
            query_request = QueryRequest(
                question=question,
                channel_id=chat_id,
                timestamp=datetime.now()
            )
            
            # Generate response
            response = buddy.answer_question(query_request, chat_context.messages)
            
            await update.message.reply_text(
                f"🤖 *Answer:*\n{response.answer}",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id
            )
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error while processing your question. Please try again."
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat_id = str(update.effective_chat.id)
        
        try:
            chat_context = self.context_manager.get_context(chat_id)
            
            if not chat_context.messages:
                await update.message.reply_text("📭 No messages tracked yet in this chat.")
                return
            
            message_count = len(chat_context.messages)
            recent_messages = chat_context.messages[-5:]  # Last 5 messages
            
            status_msg = f"📊 *Chat Status:*\n\n"
            status_msg += f"• Total messages tracked: {message_count}\n"
            status_msg += f"• Recent activity: {len(recent_messages)} messages\n\n"
            status_msg += "*Recent topics:*\n"
            
            for msg in recent_messages[-3:]:  # Show last 3
                preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                status_msg += f"• {preview}\n"
            
            await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await update.message.reply_text("❌ Error retrieving chat status.")
    
    async def actions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /actions command"""
        chat_id = str(update.effective_chat.id)
        
        try:
            actions = self.context_manager.get_unresolved_items(chat_id)
            
            if not actions:
                await update.message.reply_text("✅ No unresolved action items found!")
                return
            
            actions_msg = f"📋 *Unresolved Action Items:*\n\n"
            for i, action in enumerate(actions[:10], 1):  # Limit to 10
                actions_msg += f"{i}. {action.description}\n"
                if action.assigned_to:
                    actions_msg += f"   👤 Assigned to: {action.assigned_to}\n"
                actions_msg += f"   📅 From: {action.mentioned_at.strftime('%m/%d %H:%M')}\n\n"
            
            await update.message.reply_text(actions_msg, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error getting actions: {e}")
            await update.message.reply_text("❌ Error retrieving action items.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages in the group"""
        logger.info(f"Received message: {update.message.text[:50]}... from {update.effective_user.username}")
        
        chat_id = str(update.effective_chat.id)
        
        # Process all messages in private chats, but only activated groups
        if update.effective_chat.type in ['group', 'supergroup']:
            if int(chat_id) not in self.active_groups:
                logger.info(f"Bot not activated in group {chat_id}, ignoring message")
                return
        
        # Create message object
        message = Message(
            content=update.message.text,
            timestamp=datetime.now(),
            source="telegram",
            channel_id=chat_id,
            user_id=str(update.effective_user.id),
            message_id=str(update.message.message_id),
            metadata={
                "username": update.effective_user.username or "Unknown",
                "first_name": update.effective_user.first_name or "Unknown",
                "chat_title": update.effective_chat.title or "Private Chat"
            }
        )
        
        logger.info(f"Processing message from {message.metadata['username']}: {message.content[:50]}...")
        
        # ALWAYS store message in context (this was the bug!)
        self.context_manager.add_message(message)
        logger.info(f"Message added to context for channel {chat_id}")
        
        # Check if bot was mentioned or should respond
        bot_mentioned = "@BuddianBot" in update.message.text or "@buddianbot" in update.message.text.lower()
        should_respond = self.response_engine.should_respond(message, bot_mentioned)
        
        logger.info(f"Bot mentioned: {bot_mentioned}, Should respond: {should_respond}")
        
        # Only respond if explicitly mentioned or asked a question, but ALWAYS track the message
        if should_respond:
            buddy = self._get_buddy_agent()
            if buddy:
                try:
                    from ..models.context import QueryRequest
                    
                    if bot_mentioned:
                        contextual_question = message.content.replace("@BuddianBot", "").replace("@buddianbot", "").strip()
                        if not contextual_question or len(contextual_question) < 5:
                            contextual_question = "What should I help with?"
                    else:
                        contextual_question = message.content
                    
                    query_request = QueryRequest(
                        question=contextual_question,
                        project_id=chat_id,
                        channel_id=chat_id,
                        timestamp=datetime.now()
                    )
                    
                    chat_context = self.context_manager.get_context(chat_id)
                    response_obj = buddy.answer_question(query_request, chat_context.messages)
                    
                    if response_obj and response_obj.answer:
                        answer = response_obj.answer.strip()
                        
                        if len(answer) > 20:
                            logger.info(f"Sending response: {answer[:50]}...")
                            await update.message.reply_text(
                                f"🤖 {answer}",
                                reply_to_message_id=update.message.message_id
                            )
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
            else:
                logger.warning("BuddyAgent not available")
    
    def run(self):
        """Start the Telegram bot"""
        logger.info("Starting Telegram Buddy AI bot...")
        self.application.run_polling(drop_pending_updates=True)

# app/services/response_engine.py - Add this method
class ResponseEngine:
    def __init__(self):
        pass
    
    def should_respond(self, message: Message, bot_mentioned: bool = False) -> bool:
        """Determine if the bot should respond to this message"""
        content = message.content.lower()
        
        # Always respond if bot is mentioned
        if bot_mentioned:
            return True
        
        # Respond to questions
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        if any(indicator in content for indicator in question_indicators):
            return True
        
        # Respond to help requests
        help_indicators = ['help', 'stuck', 'problem', 'issue', 'error']
        if any(indicator in content for indicator in help_indicators):
            return True
        
        # Don't respond to everything (avoid spam)
        return False

# app/agents/buddy_agent.py - Add this method to your existing BuddyAgent class
def generate_contextual_response(self, message: Message, context) -> Optional[str]:
    """Generate a contextual response to a message"""
    try:
        # Create a prompt that includes recent context
        recent_messages = context.messages[-5:] if context.messages else []
        context_text = "\n".join([f"{msg.metadata.get('username', 'User')}: {msg.content}" 
                                 for msg in recent_messages])
        
        prompt = f"""
        Recent conversation context:
        {context_text}
        
        Current message: {message.content}
        From: {message.metadata.get('username', 'User')}
        
        As a helpful development team assistant, provide a brief, relevant response.
        Only respond if you can add value to the conversation.
        Keep responses concise and friendly.
        """
        
        response = self._query_llm(prompt)
        
        # Only return response if it's meaningful and not too generic
        if response and len(response.strip()) > 10:
            return response.strip()
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating contextual response: {e}")
        return None