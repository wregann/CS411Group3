<template>

  <div id="app">
    <div class="header">
      <h1 style="font-size: xxx-large">Weatherify</h1>
      <p style="font-size: large">music meets weather</p>
    </div>

    <!-- Display Information -->
    <p>Logged In: {{logged}}</p>
    <p v-if="!logged">Spotify Login Url: {{auth_url}}</p>
    <p v-if="logged">ID: {{user_id}} <br></p>

    <!-- Log in and out Buttons -->
    <button v-if="!logged" @click=spotifyLogin()>Login</button>
    <button v-if="logged" @click=logout()>Log Out</button>

    <!-- City Input -->
    <div v-if="logged" id="City_Input">
      <form v-on:submit.prevent="submit_city">
        <input type="text" placeholder="Input Closest City Here" v-model="city_string"/>
        <button type="submit">Submit City</button>
      </form>
      <p>City Found: {{city_found}}</p>
      <p>Latitude: {{lat}}, Longitude: {{long}}</p>
    </div>

    <!-- Main Creator Portion -->
    <div id="creator" v-if="logged && city_found">
      <select v-model="time_select">
        <option value="day">Day</option>
        <option value="eve">Eve</option>
        <option value="night">Night</option>
      </select>
      <form v-on:submit.prevent="submit_weather">
        <table border="1" class="center">
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
            <tr v-if="time_select == 'day'">
              <td> {{cur_mains[0]}} <br> {{cur_descs[0]}} <br> {{cur_temps[0]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="0" /></td>
              <td> {{cur_mains[1]}} <br> {{cur_descs[1]}} <br> {{cur_temps[1]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="1"/></td>
              <td> {{cur_mains[2]}} <br> {{cur_descs[2]}} <br> {{cur_temps[2]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="2"/></td>
              <td> {{cur_mains[3]}} <br> {{cur_descs[3]}} <br> {{cur_temps[3]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="3"/></td>
              <td> {{cur_mains[4]}} <br> {{cur_descs[4]}} <br> {{cur_temps[4]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="4"/></td>
            </tr>
            <tr v-if="time_select == 'eve'">
              <td>{{cur_mains[0]}} <br> {{cur_descs[0]}} <br> {{cur_temps[5]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="5" /></td>
              <td>{{cur_mains[1]}} <br> {{cur_descs[1]}} <br> {{cur_temps[6]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="6"/></td>
              <td>{{cur_mains[2]}} <br> {{cur_descs[2]}} <br> {{cur_temps[7]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="7"/></td>
              <td>{{cur_mains[3]}} <br> {{cur_descs[3]}} <br> {{cur_temps[8]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="8"/></td>
              <td>{{cur_mains[4]}} <br> {{cur_descs[4]}} <br> {{cur_temps[9]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="9"/></td>
            </tr>
            <tr v-if="time_select == 'night'">
              <td>{{cur_mains[0]}} <br> {{cur_descs[0]}} <br> {{cur_temps[10]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="10" /></td>
              <td>{{cur_mains[1]}} <br> {{cur_descs[1]}} <br> {{cur_temps[11]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="11"/></td>
              <td>{{cur_mains[2]}} <br> {{cur_descs[2]}} <br> {{cur_temps[12]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="12"/></td>
              <td>{{cur_mains[3]}} <br> {{cur_descs[3]}} <br> {{cur_temps[13]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="13"/></td>
              <td>{{cur_mains[4]}} <br> {{cur_descs[4]}} <br> {{cur_temps[14]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="14"/></td>
            </tr>
         
          </tbody>
        </table>
        <button>Submit Weather To Make Playlist!</button>
      </form>
    </div>
    <p v-if="city_found && logged">Created: {{playlist_created}}</p>
    <p v-if="city_found && logged">Playlist Name: {{playlist_name}}</p>
    <p v-if="city_found && logged">Created At: {{created_when}}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  el: '#app',
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
        cur_temps: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

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
              this.cur_temps[i] = response.data.daily[i].feels_like.day
              this.cur_temps[i + 5] = response.data.daily[i].feels_like.eve
              this.cur_temps[i + 10] = response.data.daily[i].feels_like.night
            }
          };
          })
        }
        catch(err){
          console.log(err)
        }
      },
      submit_weather() {
        console.log(this.selected_day)
        try {
          if (this.selected_day >= 0 && this.selected_day <= 14){
            axios.post('http://127.0.0.1:1000/api/go', {withCredentials : true,
                      main: this.cur_mains[this.selected_day % 5],
                      description: this.cur_descs[this.selected_day % 5],
                      temperature: this.cur_temps[this.selected_day]
                    }).then(response => {this.playlist_created = response.data.Created; this.playlist_name = response.data.Name; this.created_when = response.data.when})
          }
        }
        catch(err) {
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
}
table {
    margin-top: 1%;
    box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.2), 0 5px 5px 0 rgba(0, 0, 0, 0.24);
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
</style>
