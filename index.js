const fs = require('fs');
const readline = require('readline');
const {google} = require('googleapis');
const {PythonShell} = require('python-shell');
// If modifying these scopes, delete token.json.
const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
// The file token.json stores the user's access and refresh tokens, and is
// created automatically when the authorization flow completes for the first
// time.
const TOKEN_PATH = 'token.json';

const argument = process.argv[2];


// Load client secrets from a local file.
fs.readFile('credentials.json', (err, content) => {
  if (err) return console.log('Error loading client secret file:', err);
  // Authorize a client with credentials, then call the Gmail API.
  authorize(JSON.parse(content), start);
});

/**
 * Create an OAuth2 client with the given credentials, and then execute the
 * given callback function.
 * @param {Object} credentials The authorization client credentials.
 * @param {function} callback The callback to call with the authorized client.
 */
function authorize(credentials, callback) {
  const {client_secret, client_id, redirect_uris} = credentials.installed;
  const oAuth2Client = new google.auth.OAuth2(
      client_id, client_secret, redirect_uris[0]);

  // Check if we have previously stored a token.
  fs.readFile(TOKEN_PATH, (err, token) => {
    if (err) return getNewToken(oAuth2Client, callback);
    oAuth2Client.setCredentials(JSON.parse(token));
    callback(oAuth2Client);
  });
}

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 * @param {google.auth.OAuth2} oAuth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback for the authorized client.
 */
function getNewToken(oAuth2Client, callback) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  console.log('Authorize this app by visiting this url:', authUrl);
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  rl.question('Enter the code from that page here: ', (code) => {
    rl.close();
    oAuth2Client.getToken(code, (err, token) => {
      if (err) return console.error('Error retrieving access token', err);
      oAuth2Client.setCredentials(token);
      // Store the token to disk for later program executions
      fs.writeFile(TOKEN_PATH, JSON.stringify(token), (err) => {
        if (err) return console.error(err);
        console.log('Token stored to', TOKEN_PATH);
      });
      callback(oAuth2Client);
    });
  });
}


async function start(auth){
  const messageID = await getID(auth, argument);

  const messageToEval = await getMessage(auth, messageID);

  await naiveBayes(messageToEval);
}

function getID(auth, index) {
  return new Promise((resolve, reject) =>{
    const gmail = google.gmail({version: 'v1', auth});
    // Find ID of message given index starting from latest message
    gmail.users.messages.list({
      userId: 'me',
      maxResults: index+1,
    }, (err, res) => {
      if (err) reject("API ERROR");
      const messages = res.data.messages;
      if (messages.length) {
        var messageID = messages[index].id;
        resolve(messageID);
      } else {
        reject("No messages found");
      }
    });
  });
}

function getMessage(auth, messageID){
  return new Promise((resolve, reject) => {
    const gmail = google.gmail({version: 'v1', auth});
    //Retrieve message from ID
    gmail.users.messages.get({
      userId: 'me',
      id: messageID,
    }, (err, res) => {
      if (err) reject("API ERROR");

      let data = "";
      //Gmail API JSON objects are not standardized for where message data can be found, try both:
      try{
        data = JSON.stringify(res.data.payload.parts[0].body.data); //Plain text emails
      }catch(error){
        data = JSON.stringify(res.data.payload.body.data); //Heavily formatted emails
      }

      let buffer = new Buffer.from(data, "base64");
      var messageString = buffer.toString();
      resolve(messageString);
    });

  });
}

function naiveBayes(str){
  return new Promise((resolve, reject) =>{
    var pyshell = new PythonShell('./data/naivebayes.py');

    pyshell.send(str);

    pyshell.on('message', function (message) {
      console.log(message);
      resolve(message);
    });
    
    // end the input stream and allow the process to exit
    pyshell.end(function (err) {
      if (err) reject(err);
    });
  });
}