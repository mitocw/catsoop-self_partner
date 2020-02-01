'''
Question type which handles self-partner selection for groups

notes:

http://localhost:6010/_util/api/groups/get_my_group
http://localhost:6010/_util/api/groups/list_groups

'''
import string
import random
import logging
import datetime

from catsoop import cslog

LOGGER = logging.getLogger("cs")
THE_SECTION = "default"			# name of section to use for all users

MAX_GROUP_SIZE = 2			# set to None for unlimited group sizes

def js_files(context):
    return ["COURSE/__QTYPES__/self_partner/self_partner.js"]
    # % context['cs_course']]

defaults = {
    "csq_soln": "{}",
    "csq_check_function": lambda sub, soln: sub["circuit"] == soln["circuit"],
    "csq_npoints": 1,
    "csq_msg_function": lambda sub, soln: "",
    "csq_show_check": False,
}

def total_points(**info):
    return 0

def get_groups():
    context = globals()
    ginfo = csm_groups.list_groups(context, cs_path_info)
    # ginfo is dict: {section_name: { group_name: [ username, ... ] }}
    return ginfo

def canonicalize_group_name(gn):
    gn = gn.replace(' ', '_')
    gn = gn[:40]
    rndstr = ''.join(random.choice(string.digits) for _ in range(4))
    gn = "%s_%s" % (gn, rndstr)
    return gn

def get_known_group_names():
    known_groups = []
    for section, groups in get_groups().items():
        known_groups += list(groups.keys())
    return known_groups

def create_unique_group(requested_group_name):
    gn = make_unique_group_name(requested_group_name)
    return do_join_group(gn, require_exists=False)

def get_my_group_name():
    ginfo = get_groups()
    sec_ginfo = ginfo.get(THE_SECTION, {})
    for gn, users in sec_ginfo.items():	# remove user from other groups
        if cs_username in users:
            return gn, users
    return None, None

def make_unique_group_name(requested_group_name):
    known_groups = get_known_group_names()
    cnt = 100
    while cnt:
        gn = canonicalize_group_name(requested_group_name)
        if gn not in known_groups:
            return gn
        cnt = cnt - 1
    msg = '[self_partner] Error!  Could not make unique group name "%s"'
    LOGGER.error(msg)
    raise Exception(msg)

def do_remove_from_group():
    ginfo = get_groups()
    sec_ginfo = ginfo.get(THE_SECTION, {})
    rgn = []
    for ogn, users in sec_ginfo.items():	# remove user from other groups
        if cs_username in users:
            users.remove(cs_username)
            LOGGER.info('[self_partner] remmoving %s from group %s' % (cs_username, ogn))
            rgn.append(ogn)
    csm_groups.overwrite_groups(globals(), cs_path_info, THE_SECTION, sec_ginfo)
    return ','.join(rgn)

def do_join_group(gn, require_exists=True):
    ginfo = get_groups()
    if not THE_SECTION in ginfo:
        ginfo[THE_SECTION] = {}
    sec_ginfo = ginfo.get(THE_SECTION, {})
    if require_exists and (not gn in sec_ginfo):
        return None, None

    current_group_size = len(sec_ginfo.get(gn, []))
    if MAX_GROUP_SIZE and current_group_size >= MAX_GROUP_SIZE:
        LOGGER.info('[self_partner] prevented %s from joining group %s, already at size %s' % (cs_username, gn, current_group_size))
        return "max_limit", None

    for ogn, users in sec_ginfo.items():	# remove user from other groups
        if cs_username in users:
            users.remove(cs_username)
            LOGGER.info('[self_partner] remmoving %s from group %s' % (cs_username, ogn))

    toremove = []
    for ogn, users in sec_ginfo.items():	# remove empty groups
        if not len(users):
            toremove.append(ogn)
    for ogn in toremove:
        sec_ginfo.pop(ogn)

    if not gn in sec_ginfo:
        sec_ginfo[gn] = [cs_username]
    else:
        sec_ginfo[gn].append(cs_username)
    
    csm_groups.overwrite_groups(globals(), cs_path_info, THE_SECTION, sec_ginfo)
    return gn, sec_ginfo[gn]	# group name, list of usernames in group
    

def handle_submission(submissions, **info):
    LOGGER.info('[self_parnter] Received submissions=%s' % submissions)
    name = info["csq_name"]
    cnames = ["__%s_%04d" % (name, x) for x in range(3)]

    msg = ""
    requested_group_name = submissions[cnames[0]]
    group_to_join = submissions[cnames[1]]
    do_remove = submissions.get(cnames[2])

    group_name = None
    if group_to_join:
        gn, group_members = do_join_group(group_to_join)
        if group_members:
            msg += "<p>You have joined the group '%s' for this assignment</p>" % group_to_join
            msg += "<p>The group currently has as members:<ul>"
            for gm in group_members:
                msg += "<li>%s</li>" % gm
            msg += "</ul></p>"
        elif gn=="max_limit":
            msg += "<p><font color='red'>Error, could not join the group '%s'</font></p>" % group_to_join
            msg += "<p>The group is already at the maximum limit of %s persons</p>" % MAX_GROUP_SIZE
        else:
            msg += "<p><font color='red'>Error, could not join the group '%s'</font></p>" % group_to_join
            msg += "<p>Has the group been created?</p>"

    elif do_remove=="remove":
        ret = do_remove_from_group()
        if ret:
            msg += "<p>Removed from group %s</p>" % ret
        else:
            msg += "<p>Not removed from any groups</p>"

    elif len(requested_group_name) < 4:
        msg += "<p>Please enter at least 4 letters or numbers for your unique group name"
    else:
        group_name, users = create_unique_group(requested_group_name)
    if 0:	# debugging
        msg += "<p>submission: <pre>%s</pre></p>" % str(submissions)
        msg += "<p>groups: <pre>%s</pre></p>" % str(get_groups())
    if group_name:
        msg += "<p>Your registered unique group name is: <font color='blue' size='+3'>%s</font></p>" % group_name
        msg += "<p>Please ask your group partners to enter this group name to join the group.  (You are already now in the group.)</p>"
    msg += "<script type='text/javascript'>SP.hide()</script>"

    return {"score": 1, "msg": msg}

def render_html(last_log, **info):
    last_log = last_log or {}
    name = info["csq_name"]
    cnames = ["__%s_%04d" % (name, x) for x in range(3)]

    out = '<div id="%s" name="%s" class="self_partner">' % (name, name)
    out += "<h3>Self-Partner Group</h3>"
    out += "<p>Working in a group?  Let us know who you are, so that you can be checked off together!</p>"
    out += "<p>Instructions: (1) <b>One</b> of you should <a href='#' id='sp_create_group_link'>create a group</a>.</p>"
    out += "<div id='sp_create_group' style='display:none;background:#ff0;padding:10px;border-radius:15px'>"
    out += "Enter a unique name for your group: <input id='%s' name='%s' type='text' size='40' style='font-size:18px;'/></p>" % (cnames[0], cnames[0])
    out += "<br/>(letters, numbers, and underscores only, please)"
    out += "</div>"
    out += "<p>(2) Each group member should then enter the given new group name into the box below.<br/>"
    out += "&nbsp; Name of group to join: <input id='%s' name='%s' type='text' size='40' style='font-size:18px;'/></p>" % (cnames[1], cnames[1])
    out += "<p>Reload this page anytime to refresh your group status (and to get a delete button, if you want to remove yourself from a group you've joined).</p>"
    if MAX_GROUP_SIZE:
        out += "<p>Groups are limited to <font color='red'>%s persons max</font> each, so that checkoff discussions can be inclusive.</p>" % MAX_GROUP_SIZE
    out += "</div>"
    my_gn, group_members = get_my_group_name()
    if not my_gn:
        out += "<div id='sp_current_group' style='background:#fec;padding:10px;border-radius:15px'>"
        out += "You are not currently in any group"
    else:
        out += "<div id='sp_current_group' style='background:#cfc;padding:10px;border-radius:15px'>"
        out += "<p>You are currently in group <font size='+3' color='blue'>%s</font> for this assignment</p> " % (my_gn)
        out += "<p>The group currently has as members:<ul>"
        for gm in group_members:
            out += "<li>%s</li>" % gm
        out += "</ul></p>"
        out += "<input id='%s' name='%s' type='hidden' value='' style='font-size:18px;'/>" % (cnames[2], cnames[2])
        out += '<button class="btn btn-catsoop" id="sp_remove_from_group">Remove me from the group</button>'
    out += "</div>"


    return out + (
        '\n<script type="text/javascript">'
        'document.addEventListener("DOMContentLoaded", function(){'
        "    SP.setup('%s');"
        "});"
        "</script>" % name
    )

def answer_display(**info):
    out = "Solution: %s" % (info["csq_soln"])
    return out
