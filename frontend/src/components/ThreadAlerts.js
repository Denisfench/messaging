import React, { Component } from 'react'
import axios from 'axios';
import { Loader, Dimmer, Table } from 'semantic-ui-react' 
import createHistory from "history/createBrowserHistory"
import { withRouter } from 'react-router-dom';

const history = createHistory()

class ThreadAlerts extends Component {

    state = {
        loadingData: false, 
        alerts: [],
    };

    background = {
        "Low": "#FFFFFF",
        "Medium": "#FFCC00",
        "High": "#FF0000",
    };

    apiServer = 'https://socnet.pythonanywhere.com/';

    async componentDidMount() {
        try {
            this.setState({ loadingData: true });
            const payload = await axios.get(`${this.apiServer}alerts`) 
            this.setState ({
                loadingData: false,
                alerts: payload.data,
            });
        } catch(e) {
            console.log('Error while fetching alterts')
        }
    }
    

    renderTableData = () => {
        return this.state.alerts.map((alertData) => {
            const id = alertData[0]
            const date = alertData[1]
            const region = alertData[4]
            const title = alertData[6]
            const description = alertData[7]

            const bgcolor = this.background

            return (
                <Table.Row style={{background: bgcolor[alertData[8]]}} onClick = {() => {this.props.history.push(`/thread/${id}`)}}>
                {/* <Table.Row >  */}
                    <Table.Cell> {title} </Table.Cell>
                    <Table.Cell> {description} </Table.Cell>
                    <Table.Cell> {region} </Table.Cell>
                    <Table.Cell textAlign="right"> {date} </Table.Cell>
                </Table.Row>
            )
        })
    }

    render() {

        const { loadingData, alerts } = this.state;
        
        if (loadingData) {
            return (
                <Dimmer active inverted>
                    <Loader size="massive"> Loading: fetching alerts..</Loader>
                </Dimmer>
            )
        }

        return (
            <div style={{padding: "2%"}}>
                <Table fixed singleLine padded selectable color="teal">
                    <Table.Header>
                        <Table.HeaderCell> Type </Table.HeaderCell>
                        <Table.HeaderCell width={6}> Description </Table.HeaderCell>
                        <Table.HeaderCell> Region </Table.HeaderCell>
                        <Table.HeaderCell textAlign="right"> Date </Table.HeaderCell>
                    </Table.Header>
                    <Table.Body>
                        {/* { alerts.map((eventData) => {
                            return (
                                <AlertsCard data={eventData} />
                            )}
                        )}; */}
                        { this.renderTableData() }
                    </Table.Body>
                </Table>
            </div>
        )
    }
}

export default withRouter(ThreadAlerts);