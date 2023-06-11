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

function formatProgress() {
    var downloaded = (props.job.progress_tweets_downloaded > 0 || props.job.progress_likes_downloaded > 0)
    var deleted = (props.job.progress_tweets_deleted > 0 || props.job.progress_retweets_deleted > 0 || props.job.progress_likes_deleted > 0 || props.job.progress_dms_deleted > 0 || props.job.progress_dms_skipped > 0)

    var progress = ""

    if (downloaded) {
        progress += "Downloaded "
        if (props.job.progress_tweets_downloaded > 0) {
            progress += props.job.progress_tweets_downloaded.toLocaleString("en-US") + " tweets, "
        }
        if (props.job.progress_likes_downloaded !== undefined) {
            progress += props.job.progress_likes_downloaded.toLocaleString("en-US") + " likes, "
        }
    }
    if (deleted) {
        if (downloaded) {
            progress += "and deleted "
        } else {
            progress += "Deleted "
        }
        if (props.job.progress_tweets_deleted > 0) {
            progress += props.job.progress_tweets_deleted.toLocaleString("en-US") + " tweets, "
        }
        if (props.job.progress_retweets_deleted > 0) {
            progress += props.job.progress_retweets_deleted.toLocaleString("en-US") + " retweets, "
        }
        if (props.job.progress_likes_deleted > 0) {
            progress += props.job.progress_likes_deleted.toLocaleString("en-US") + " likes, "
        }
        if (props.job.progress_dms_deleted > 0 || props.job.progress_dms_skipped > 0) {
            progress += props.job.progress_dms_deleted.toLocaleString("en-US") + " DMs"
            if (props.job.progress_dms_skipped > 0) {
                progress += " (skipped " + props.job.progress_dms_skipped.toLocaleString("en-US") + ")"
            }
        }
    }

    if (progress.endsWith(", ")) {
        progress = progress.substring(0, progress.length - 2)
    }

    return progress
}

function scheduledTimestampInThePast() {
    if (props.job['scheduled_timestamp'] == undefined) {
        return true
    } else {
        return Math.floor(props.job['scheduled_timestamp'] * 1000) <= Date.now()
    }
}

function cancelJob() {
    if (confirm("Are you sure you want to cancel this job?")) {
        fetch("/api/jobs/" + props.job.id + "/cancel", { method: "POST" }).then(response => {
            if (response.ok) {
                location.reload()
            } else {
                alert("Failed to cancel job")
            }
        })
    }
}
</script>

<template>
    <div :class="job.status">
        <template v-if="job.status == 'pending'">
            <template v-if="job.job_type == 'download'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to download all of your tweets and likes
                </p>
                <p class="status" v-else>
                    Waiting to download all of your tweets and likes, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete_dms'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete all of your old direct messages
                </p>
                <p class="status" v-else>
                    Waiting to delete all of your old direct messages, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete_dm_groups'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete all of your old group direct messages
                </p>
                <p class="status" v-else>
                    Waiting to delete all of your old group direct messages, scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <template v-else-if="job.job_type == 'delete'">
                <p class="status" v-if="scheduledTimestampInThePast()">
                    Waiting to delete your old tweets, likes, and/or direct messages
                </p>
                <p class="status" v-else>
                    Waiting to delete your old tweets, likes, and/or direct messages,
                    scheduled for
                    <em>{{ humanReadableTimestamp(job.scheduled_timestamp) }}</em>
                </p>
            </template>
            <p><button class="secondary" v-on:click="cancelJob()">Cancel Job</button></p>
        </template>

        <template v-else-if="job.status == 'active'">
            <p class="status">{{ job.progress_status }}</p>
            <p class="progress">
                Started
                <em>{{ humanReadableTimestamp(job.started_timestamp) }}</em>
                <br />{{ formatProgress() }}
            </p>
            <p><button class="secondary" v-on:click="cancelJob()">Cancel Job</button></p>
        </template>

        <template v-else-if="job.status == 'finished' || job.status == 'canceled' || job.status == 'failed'">
            <p class="finished">
                <span class="finished-timestamp">{{
                    humanReadableTimestamp(job.finished_timestamp)
                }}</span>
                <span v-if="job.status == 'canceled' || job.status == 'failed'" class="canceled-or-failed-status">{{
                    job.status }}</span>
                <span class="progress">{{ formatProgress() }}</span>
                <span v-if="job.status == 'canceled' || job.status == 'failed'">{{ job.progress_status }}</span>
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

.finished .canceled-or-failed-status {
    margin-right: 0.5em;
    display: inline-block;
    font-size: 0.9em;
    color: red;
}

.finished .progress {
    font-size: 0.9em;
    color: #000000;
}
</style>