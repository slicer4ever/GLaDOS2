import glados
import asyncio


cdfs_server_id = '318450472157577218'
thecomet_id = '104330175243636736'
welcome_channel_id = '318450472157577218'
off_topic_channel_id = '318455404894093312'
verified_horse_role_id = '318452319358550036'


def check_message_for_deletion(message):
    # Delete all messages unless they are from TheComet
    if message.author.id == thecomet_id:
        return False
    return True


class Verify(glados.Module):
    def get_help_list(self):
        return tuple()

    def setup_global(self):
        @self.client.event
        @asyncio.coroutine
        def on_member_remove(member):
            if member.server is None or member.server.id != cdfs_server_id:
                return tuple()
            channel = self.client.get_channel(off_topic_channel_id)
            if channel is None:
                glados.log('ERROR: Failed to retrieve off-topic channel')
                return tuple()
            yield from self.client.send_message(channel, "{} left the server!".format(member.name))

    @glados.Module.commands('verify')
    def verify(self, message, arg):
        if message.channel.id != welcome_channel_id:
            return tuple()

        if arg != 'I accept these rules and I understand that breaking said rules will result in a ban from this server':
            yield from self.client.send_message(message.channel, 'Invalid! Make sure you typed the text exactly')
            return

        cdfs_server = self.client.get_server(cdfs_server_id)
        roles = [role for role in cdfs_server.roles if role.id == verified_horse_role_id]
        if len(roles) == 0:
            yield from self.client.send_message('Hmm, couldn\'t find the role ID. Contact an admin')
        yield from self.client.add_roles(message.author, *roles)

        yield from self.client.send_message(message.channel, 'Hooray! You\'re a verified horse now {}!'.format(message.author.name))

        # Let people know in off-topic
        off_topic_channel = self.client.get_channel(off_topic_channel_id)
        if off_topic_channel is None:
            glados.log('ERROR: Failed to retrieve off-topic channel')
            return tuple()

        yield from self.client.send_message(off_topic_channel, '{} joined the server! If you are especially kinky, contact an admin for access to the #fetish channel. Type ``.help`` for a list of bot commands.'.format(message.author.mention))

    @asyncio.coroutine
    def clean_up_shit_messages(self):
        welcome_channel = self.client.get_channel(welcome_channel_id)
        if welcome_channel is None:
            glados.log('ERROR: Failed to retrieve welcome channel')
            return tuple()

        yield from asyncio.sleep(15)  # allow people to read the message
        yield from self.client.purge_from(welcome_channel, check=check_message_for_deletion)

    @glados.Module.rules('^.*$')
    def delete_this(self, message, match):
        asyncio.ensure_future(self.clean_up_shit_messages())
        return tuple()
