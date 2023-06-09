<script setup>
const props = defineProps({
    job: Object
})

function humanReadableTimestamp(timestamp) {
    if (timestamp == null) {
        return "null"
    }
    var date = new Date(timestamp * 1000)
    return date.toLocaleDateString() + " at " + date.toLocaleTimeString()
}

function progressStatus() {
    try {
        var p = JSON.parse(props.job.data)
        if (Object.hasOwn(p, "progress")) {
            if (Object.hasOwn(p['progress'], "status")) {
                return p['progress']['status']
            } else {
                return "Active"
            }
        }
    } catch (error) {
        console.log("JSON decoding error:", error, props.job.data)
        return ""
    }
}

function formatProgress() {
    try {
        var p = JSON.parse(props.job.data)
        if (Object.hasOwn(p, "progress")) {
            var tweetsFetched = p['progress']['tweets_fetched']
            var likesFetched = p['progress']['likes_fetched']
            var tweetsDeleted = p['progress']['tweets_deleted']
            var retweetsDeleted = p['progress']['retweets_deleted']
            var likesDeleted = p['progress']['likes_deleted']
            var dmsDeleted = p['progress']['dms_deleted']
            var dmsSkipped = p['progress']['dms_skipped']

            var downloaded = (tweetsFetched !== undefined || likesFetched !== undefined)
            var deleted = (tweetsDeleted !== undefined || retweetsDeleted !== undefined || likesDeleted !== undefined || dmsDeleted !== undefined || dmsSkipped !== undefined)

            var progress = ""

            if (downloaded) {
                progress += "Downloaded "
                if (tweetsFetched !== undefined) {
                    progress += tweetsFetched.toLocaleString("en-US") + " tweets, "
                }
                if (likesFetched !== undefined) {
                    progress += likesFetched.toLocaleString("en-US") + " likes, "
                }
            }
            if (deleted) {
                if (downloaded) {
                    progress += "and deleted "
                } else {
                    progress += "Deleted "
                }
                if (tweetsDeleted !== undefined) {
                    progress += tweetsDeleted.toLocaleString("en-US") + " tweets, "
                }
                if (retweetsDeleted !== undefined) {
                    progress += retweetsDeleted.toLocaleString("en-US") + " retweets, "
                }
                if (likesDeleted !== undefined) {
                    progress += likesDeleted.toLocaleString("en-US") + " likes, "
                }
                if (dmsDeleted !== undefined) {
                    progress += dmsDeleted.toLocaleString("en-US") + " DMs"
                    if (dmsSkipped !== undefined) {
                        progress += " (skipped " + dmsSkipped.toLocaleString("en-US") + ")"
                    }
                }
            }

            if (progress.endsWith(", ")) {
                progress = progress.substring(0, progress.length - 2)
            }

            return progress
        }
    } catch (error) {
        console.log("JSON decoding error:", error, props.job.data)
        return ""
    }
}

function scheduledTimestampInThePast() {
    if (props.job['scheduled_timestamp'] == undefined) {
        return true
    } else {
        return Math.floor(props.job['scheduled_timestamp'] * 1000) <= Date.now()
    }
}
</script>

<template>
    <div :class="job.status">
        <template v-if="job.status == 'pending'">
            <template v-if="job.job_type == 'fetch'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to download all of your tweets and likes as soon as it's your
                    turn in the queue
                </p>
                <p class="status" v-else>
                    Waiting to download all of your tweets and likes, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete_dms'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete all of your old direct messages as soon as it's your
                    turn in the queue
                </p>
                <p class="status" v-else>
                    Waiting to delete all of your old direct messages, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete_dm_groups'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete all of your old group direct messages as soon as
                    it's your turn in the queue
                </p>
                <p class="status" v-else>
                    Waiting to delete all of your old group direct messages, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete your old tweets, likes, and/or direct messages as
                    soon as it's your turn in the queue
                </p>
                <p class="status" v-else>
                    Waiting to delete your old tweets, likes, and/or direct messages,
                    scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
        </template>

        <template v-else-if="job.status == 'active'">
            <p class="status">{{ progressStatus() }}</p>
            <p class="progress">
                Started
                <em>{{ humanReadableTimestamp(job.started_timestamp) }}</em>
                <br />{{ formatProgress() }}
            </p>
        </template>

        <template v-else-if="job.status == 'finished'">
            <p class="finished">
                <span class="finished-timestamp">{{
                        humanReadableTimestamp(job.finished_timestamp)
                }}</span>
                <span class="progress">{{ formatProgress() }}</span>
            </p>
        </template>
    </div>
</template>

<style scoped>
.label {
    display: inline-block;
    width: 60px;
    text-align: right;
    font-size: 11px;
    font-weight: bold;
}

.status {
    color: #666666;
    font-size: 12px;
}

.active p.progress {
    display: inline-block;
    border: 1px solid #5d8fad;
    padding: 10px;
    margin: 0;
    border-radius: 10px;
    background-color: #dbf2ff;
}

.finished .finished-timestamp {
    margin-right: 0.5em;
    display: inline-block;
    font-size: 0.9em;
    color: #999999;
}

.finished .progress {
    font-size: 0.9em;
    color: #000000;
}
</style>