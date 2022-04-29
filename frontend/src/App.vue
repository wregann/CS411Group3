<template>

  <div id="app">
    <div class="header">
      <h1 style="font-size: xxx-large">Weatherify</h1>
      <p style="font-size: large">music meets weather</p>
    </div>

    
    <!-- Display Information -->
    <h2 class="gray-text" style="color: dimgray;">1: Log Into Spotify!</h2>
    <!-- <p>Logged In: {{logged}}</p> -->
    <!-- <p v-if="!logged">Spotify Login Url: {{auth_url}}</p> -->
    

    <!-- Log in and out Buttons -->
    <b-button variant="success" v-if="!logged" @click=spotifyLogin()>Login</b-button>
    <b-button variant="success" v-if="logged" @click=logout()>Log Out</b-button>
    <p v-if="logged" style="margin-top: 5px;">Logged In With ID: {{user_id}} <br></p>
    <div class="checkmark" v-if="logged"></div>
    <p class="bigRedX" v-if="!logged">X</p>

    <hr class="rounded">
    <h2 class="gray-text" style="color: dimgray;">2: Input a City Close to You!</h2>
    <!-- City Input -->
    <div v-if="logged" id="City_Input">
      <form v-on:submit.prevent="submit_city">
        <input type="text" placeholder="Input Closest City Here" v-model="city_string"
        style="margin-right: 7px; height: 35px; position: relative;
        top: 3px;"/>
        <b-button type="submit" variant="success">Submit City</b-button>
      </form>
      <!-- <p>City Found: {{city_found}}</p> -->
      <p v-if="city_found"  style="margin-top: 5px;">Latitude: {{lat}}, Longitude: {{long}}</p>
      <div class="checkmark" v-if="city_found"></div>
      <p class="bigRedX" v-if="!city_found">X</p>
    </div>
    <hr class="rounded">
    <h2 class="gray-text" style="color: dimgray;">3: Choose your Weather and Create!</h2>
    <!-- Main Creator Portion -->
    <div id="creator" v-if="logged && city_found">
      Time of Day: 
      <select v-model="time_select" @change="change_day()">
        <option value="day">Day</option>
        <option value="eve">Eve</option>
        <option value="night">Night</option>
      </select>
      <form v-on:submit.prevent="submit_weather">
        <table>
          <thead>
            <tr>
                <th>{{days[0]}}</th>
                <th>{{days[1]}}</th>
                <th>{{days[2]}}</th>
                <th>{{days[3]}}</th>
                <th>{{days[4]}}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td> {{cur_mains[0]}} <br> {{cur_descs[0]}} <br> {{cur_temps[cur_temp_ind[0]]}}<span>&#176;</span> F <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="0" /></td>
              <td> {{cur_mains[1]}} <br> {{cur_descs[1]}} <br> {{cur_temps[cur_temp_ind[1]]}}<span>&#176;</span> F <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="1"/></td>
              <td> {{cur_mains[2]}} <br> {{cur_descs[2]}} <br> {{cur_temps[cur_temp_ind[2]]}}<span>&#176;</span> F <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="2"/></td>
              <td> {{cur_mains[3]}} <br> {{cur_descs[3]}} <br> {{cur_temps[cur_temp_ind[3]]}}<span>&#176;</span> F <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="3"/></td>
              <td> {{cur_mains[4]}} <br> {{cur_descs[4]}} <br> {{cur_temps[cur_temp_ind[4]]}}<span>&#176;</span> F <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="4"/></td>
            </tr>
                    
          </tbody>
        </table>
        <b-button type="submit" variant="success" style="margin-bottom: 16px;">Submit Weather To Make Playlist!</b-button>
      </form>
    </div>
    <TheLoader v-if="city_found && submit_weather_loading"/>
    <div v-if="playlist_created">
    <!-- <p v-if="city_found && logged && !submit_weather_loading">Created: {{playlist_created}}</p>-->
    <p v-if="city_found && logged && !submit_weather_loading">Playlist Name: {{playlist_name}}</p>
    <p v-if="city_found && logged && !submit_weather_loading">Created At: {{created_when}}</p>
    <div class="checkmark" v-if="playlist_created"></div>
    </div>
    <p class="bigRedX" v-if="!playlist_created && !submit_weather_loading && logged">X</p>
  </div>
</template>

<script>
import axios from 'axios';
import TheLoader from '@/components/TheLoader.vue'

export default {
  el: '#app',
  components: {
    TheLoader,
  },
  data() {
    return {
      image: {backgroundImage: "url(https://i.pinimg.com/originals/dd/14/ee/dd14ee38df85f17a1054668f74546c30.jpg)"},
      days: [],
      logged: false,
      auth_url: null,
      user_id: null,
      city_string: null,
      city_found: false,
      lat: 0,
      long: 0,
      selected_day: null,
      playlist_created: false,
      playlist_name: "",
      created_when: null,
      time_select: "day",
      cur_mains: ["", "", "", "", ""],
      cur_descs: ["", "", "", "", ""],
      cur_temps: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      submit_weather_loading: false,
      cur_temp_ind: [0,1,2,3,4],

    }
  },
  mounted() {
    axios.defaults.withCredentials=true     
    try{
      axios.get('http://127.0.0.1:1000/api/get_5_days').then(response => {console.log(response); this.days = response.data.days})
      axios.get('http://127.0.0.1:1000/api/').then(response => {this.logged = response.data.logged; this.user_id = response.data.user_id; this.auth_url = response.data.auth_url})       
    }
    catch(err){
      console.log(err)
    }
  },
  methods : {
    spotifyLogin(){
      window.location.href = this.auth_url;
    },
    logout(){
      try{
        axios.get('http://127.0.0.1:1000/api/out').then(response => 
        {console.log(response); this.logged = false; this.auth_url = null; this.user_id = null;
        this.created_when = null; this.city_found = false; this.playlist_created = false; this.playlist_name = ""; this.$router.push('/'); 
        axios.get('http://127.0.0.1:1000/api/').then(response => {this.logged = response.data.logged; this.user_id = response.data.user_id; this.auth_url = response.data.auth_url})       
        })
      }
      catch(err){
        console.log(err)
      }
    },
    submit_city() {
      try{
        console.log('http://127.0.0.1:1000/api/get_weather_data/' + this.city_string)
        axios.get('http://127.0.0.1:1000/api/get_weather_data/' + this.city_string).then(response => {console.log(response); this.lat = response.data.lat; this.long = response.data.lon; this.city_found = (this.lat) ? true : false;
        if (this.city_found) {
          for (let i = 0; i < 5; i++) {
            this.cur_mains[i] = response.data.daily[i].weather[0].main
            this.cur_descs[i] = response.data.daily[i].weather[0].description
            this.cur_temps[i] = Math.round((response.data.daily[i].feels_like.day - 273.15) * 9 / 5 + 32)
            this.cur_temps[i + 5] = Math.round((response.data.daily[i].feels_like.eve - 273.15) * 9 / 5 + 32)
            this.cur_temps[i + 10] = Math.round((response.data.daily[i].feels_like.night - 273.15) * 9 / 5 + 32)
          }
        };
        })
      }
      catch(err){
        console.log(err)
      }
    },
    change_day() {
      console.log("Changed Day")
      if (this.time_select == 'day') {
        this.cur_temp_ind = [0,1,2,3,4]
      }
      else if (this.time_select == 'eve'){
        this.cur_temp_ind = [5,6,7,8,9]
      }
      else {
        this.cur_temp_ind = [10,11,12,13,14]
      }
    },
    submit_weather() {
      this.submit_weather_loading = true
      console.log(this.selected_day)
      try {
        if (this.selected_day >= 0 && this.selected_day <= 14){
          axios.post('http://127.0.0.1:1000/api/go', {withCredentials : true,
                    main: this.cur_mains[this.selected_day],
                    description: this.cur_descs[this.selected_day],
                    temperature: this.cur_temps[this.cur_temp_ind[this.selected_day]]
                  }).then(response => {this.playlist_created = response.data.Created; this.playlist_name = response.data.Name; this.created_when = response.data.when;this.submit_weather_loading = false})
        }
      }
      catch(err) {
        this.submit_weather_loading = false
        console.log(err)
      }
    }
  }
}
</script>

<style>
#app {
  text-align: center;
  color: #2c3e50;
}
.image {
      height: 500px;
      margin-left: 200px;
      margin-right: 200px;
      background-repeat: no-repeat;
  }
.header {
    padding: 5px;
    text-align: center;
    background: #0baff0;
    color: whitesmoke;
    margin-bottom: 20px;
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}
table {
    margin-top: 5px;
    box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.2), 0 5px 5px 0 rgba(0, 0, 0, 0.24);
    border: 50px rgb(0, 0, 0);
    border-collapse: collapse; 
    text-align: center;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 15px;
}
table th {
    padding-left: 30px;
    padding-right: 30px;
    padding-top: 10px;
    padding-bottom: 10px;
    text-align: center;
    color: #000000;
}
table td{
    align-items: center;
    white-space: nowrap;
    text-align: center;
    color: #000000;
}
.center {
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}
/* Rounded border */
hr.rounded {
  border-top: 3px solid #bbb;
}
.checkmark {
      display: inline-block;
      transform: rotate(45deg);
      height: 45px;
      width: 20px;
      border-bottom: 7px solid #78b13f;
      border-right: 7px solid #78b13f;
      margin-left: auto;
      margin-right: auto;
}
.bigRedX {
  color: red;
  margin-left: auto;
  margin-right: auto;
  font-size: 60px;
  font-weight: bold;
}
</style>
