<script setup>
import { ref } from "vue"

const testCredentialsLoading = ref(false)
const errorMessage = ref("")
const twitterApiKey = ref("")
const twitterApiSecret = ref("")
const twitterAccessToken = ref("")
const twitterAccessTokenSecret = ref("")

function testCreds() {
    testCredentialsLoading.value = true
    fetch("/api/test-creds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            twitter_api_key: twitterApiKey.value,
            twitter_api_secret: twitterApiSecret.value,
            twitter_access_token: twitterAccessToken.value,
            twitter_access_token_secret: twitterAccessTokenSecret.value
        }),
    })
        .then(function (response) {
            testCredentialsLoading.value = false
            response.json().then(function (data) {
                if (data.error) {
                    errorMessage.value = data['error_message']
                } else {
                    errorMessage.value = ""
                    alert("Your Twitter API credentials are valid!")
                    window.location.href = "/settings"
                }
            })
        })
        .catch(function (err) {
            console.log("Error testing credentials", err)
            errorMessage.value = err
            testCredentialsLoading.value = false
        })
}
</script>

<template>
    <div>
        <p class="center"><img class="logo" src="/images/logo.png" alt="Semiphemeral" /></p>
        <form v-on:submit.prevent="onSubmit">
            <p class="larger">Semiphemeral uses the Twitter API. Since Elon Musk took over Twitter, the
                billionaire ended
                free access to the
                API in an attempt to squeeze every penny out its users. However, it's still possible for
                individual
                users to get API keys for free to use for their own accounts. Follow these steps to make your own Twitter
                API key.</p>
            <p><strong>Step 1:</strong> Load the <a href="https://developer.twitter.com/en/portal">Twitter Developer
                    Portal</a>. It will try to charge you absurdly unreasonable amount of money, but there should be
                a tiny
                "Sign
                up for Free Account" link. Click that.</p>
            <p class="center"><img src="/images/twitter-dev-account1.png" alt="" /></p>
            <p><strong>Step 2:</strong> Next, you must fill out a form describing your use case (using over 250
                characters),
                and agree to some things.</p>
            <p class="center"><img src="/images/twitter-dev-account2.png" alt="" /></p>
            <p><strong>Step 3:</strong> You should now have access to the Twitter Developer Portal. A default
                project should
                have automatically been created for you. From the Dashboard, you should see your project's app, and
                it should
                include a "Keys and Tokens" button that's shaped like a skeleton key. Click that.</p>
            <p class="center"><img src="/images/twitter-dev-account3.png" alt="" /></p>
            <p>The Key and Tokens page should look like this:</p>
            <p class="center"><img src="/images/twitter-dev-account4.png" alt="" /></p>
            <p><strong>Step 4:</strong> Under Consumer Keys, next to "API Key and Secret", click the Regenerate
                button. It
                will ask you if you're sure. Click "Yes, regnerate". It will generate a new key for you and show you
                two
                values,
                an API Key and an API Key Secret. Copy and paste those values here.</p>
            <p>
                <label class="input" for="twitter-api-key">API Key</label>
                <input type="text" id="twitter-api-key" v-model="twitterApiKey" />
            </p>
            <p>
                <label class="input" for="twitter-api-key">API Key Secret</label>
                <input type="text" id="twitter-api-secret" v-model="twitterApiSecret" />
            </p>
            <p>Then click "Yes, I saved them".</p>
            <p><strong>Step 5:</strong> Under Authentication Tokens, next to "Access Token and Secret", click the
                Generate
                button. It will generate a new key for you and show you two
                values,
                an Access Token and an Access Token Secret. Copy and paste those values here.</p>
            <p>
                <label class="input" for="twitter-access-token">Access Token</label>
                <input type="text" id="twitter-access-token" v-model="twitterAccessToken" />
            </p>
            <p>
                <label class="input" for="twitter-access-token-secret">Access Token Secret</label>
                <input type="text" id="twitter-access-token-secret" v-model="twitterAccessTokenSecret" />
            </p>
            <p>Then click "Yes, I saved them".</p>
            <p><strong>Step 6:</strong> Once you've entered your API Key, API Key Secret, Access Token, and Access
                Token
                Secret above, click the following button to test your API credentials to see if they work.</p>
            <p>
                <button v-on:click="testCreds()" v-bind:disabled="testCredentialsLoading">Test Twitter API
                    Credentials</button>
            </p>
            <p class="error-message" v-if="errorMessage.value != ''">{{ errorMessage }}</p>
        </form>
    </div>
</template>

<style scoped>
img.logo {
    width: 200px;
    max-width: 100%;
}

p.larger {
    font-size: 135%;
}

button {
    background-color: #4caf50;
    border: none;
    color: white;
    padding: 5px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    cursor: pointer;
    font-weight: bold;
    border-radius: 5px;
    margin: 0 0 5px 0;
}

.center {
    text-align: center;
}

img {
    width: 500px;
}

label {
    display: inline-block;
    width: 200px;
    font-weight: bold;
    text-align: right;
    padding-right: 10px;
}

input[type="text"] {
    width: 400px;
}
</style>