#!/bin/sh

DATE=$(date "+%Y%m%d_%H%M%S")
BASE_PATH=$(pwd)
REPO_PATH="repos"
REPO_FILE="url_list"
OUTPUT_FILE=$BASE_PATH/"report_"$DATE".txt"

# Cleanup
# for i in `cat $REPO_FILE`; do
#    name=`basename $i`
#    test -d $REPO_PATH/$name && rm -fR $REPO_PATH/$name>/dev/null 
#done



# Retrieve branch info 
function get_branch_info() {
    echo "=== Branches ==="
    for branch in `git branch -r | grep -v HEAD`;do 
        echo -e `git show --format="%ci,%cn,<%ce>,%H" $branch| head -n 1`","$branch\
            `git branch -a --no-merged | grep $branch>/dev/null && echo ",unmerged"`; 
    done | sort -r
}

# Retrieve tag info 
function get_tag_info() {
    echo "=== Tags ==="
    for tag in `git tag -l`;do 
        echo -e `git rev-parse $tag| xargs git cat-file -p | head -n 4` \
            | awk '{print (strftime("%F %H:%M:%S %z", $(NF-1) $NF) "," $(NF-4),$(NF-3) "," $(NF-2) "," $2 "," $6 )}'
    done  
}

# Retrieve last commit info
function get_last_commit_info() {
    echo "=== Last commit ==="
    for name in `git shortlog -s -n -e --all | awk '{print $NF}'`; do 
        rev=`git log -n1 --all --committer="$name" | head -n1 | awk '/commit/{print $2}'`
        echo -e `git show --format="%ci,%cn,<%ce>,%H" $rev | head -n1`
    done | sort -r 
}

# Retrieve last month user logs
function get_last_messages() {
    echo "=== Last month messages ==="
    git shortlog --since="last month" --all --format="%h,%s"
}

# Main code
# Enable ssh agent
# env=~/.ssh/agent.env

# agent_load_env () { test -f "$env" && . "$env" >| /dev/null ; }

# agent_start () {
#     (umask 077; ssh-agent >| "$env")
#     . "$env" >| /dev/null ; }

# agent_load_env

# # agent_run_state: 0=agent running w/ key; 1=agent w/o key; 2= agent not running
# agent_run_state=$(ssh-add -l >| /dev/null 2>&1; echo $?)

# if [ ! "$SSH_AUTH_SOCK" ] || [ $agent_run_state = 2 ]; then
#     agent_start
#     ssh-add
# elif [ "$SSH_AUTH_SOCK" ] && [ $agent_run_state = 1 ]; then
#     ssh-add
# fi

#unset env

# Parse repos
for i in `cat $REPO_FILE`; do
    name=`basename $i`

    echo "***** $name ******"
#    echo "***** $name ******" >> $OUTPUT_FILE

    # Clone repo
    #git clone $i $REPO_PATH/$name

    # Check if clone was succesful
    if [ -d $REPO_PATH/$name ]; then 
        cd $REPO_PATH/$name 

        # Check if cloned repo is empty
        empty_repo=`git status | grep "No commits" | wc -l` 
        if [ 1 = $empty_repo  ]; then 
            echo "Empty repo"
#            echo "Empty repo"       >> $OUTPUT_FILE
        else
            get_branch_info         #>> $OUTPUT_FILE
            get_tag_info            #>> $OUTPUT_FILE
            get_last_commit_info    #>> $OUTPUT_FILE
            get_last_messages       #>> $OUTPUT_FILE
        fi

        cd $BASE_PATH 
    else
        echo "Failed to clone"  
#        echo "Failed to clone" >> $OUTPUT_FILE
    fi

    echo " " #>> $OUTPUT_FILE
    echo " " #>> $OUTPUT_FILE

done


