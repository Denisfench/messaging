import React, { Component } from "react";
import { Link } from 'react-router-dom';
import Card from 'react-bootstrap/Card';

class Alert extends Component {
  constructor(props){
    super(props);
    this.state = {
      eventDetails: this.props.data,
    }
    this.background = {
      "Low": "light",
      "Medium": "warning",
      "High": "danger",
    };
  }

  render() {
    const { eventDetails } = this.state;
    return (
      <Card bg={this.background[eventDetails[8]]} className="m-3">
        <Card.Header as="h5">{ eventDetails[6] }</Card.Header>
        <Card.Body>
          <Card.Title>{ eventDetails[7] }</Card.Title>
          <Card.Text>
            { `${eventDetails[3]}, ${eventDetails[4]} ${eventDetails[2]}, ${eventDetails[5]} at ${eventDetails[1]}` }
            <br />
            { `Priority: ${eventDetails[8]}` }
            <br />
            { `Author: ${eventDetails[9]}` }
          </Card.Text>
          <Link to={`/thread/${this.props.id}`}><button type="button" className="btn btn-primary">View Thread</button></Link>
        </Card.Body>
      </Card>
    );
  }
}

export default Alert;